# modules/callbacks/heatmap_callbacks.py
import dash
from dash import Input, Output, State
import plotly.graph_objects as go
from modules.data_loader import load_wifi_data, prepare_heatmap_data
from modules.config import PARAMETERS, LOCATION_PIXEL_COORDS
import pandas as pd
from modules.utils import get_pixel_coords


def register_heatmap_callbacks(dash_app, colors):
    
    # 🔁 Switch parameter using ◀️ ▶️ buttons
    @dash_app.callback(
        Output('heatmap-param-index', 'data'),
        Output('current-heatmap-param-display', 'children'),
        Output('heatmap-param', 'value'),
        Input('prev-heatmap-param', 'n_clicks'),
        Input('next-heatmap-param', 'n_clicks'),
        State('heatmap-param-index', 'data'),
        prevent_initial_call=True
    )
    def switch_heatmap_parameter(prev_clicks, next_clicks, current_index):
        ctx = dash.callback_context
        if not ctx.triggered:
            return current_index, dash.no_update, dash.no_update

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        new_index = (current_index - 1 if triggered_id == 'prev-heatmap-param' else current_index + 1) % len(PARAMETERS)
        new_param = PARAMETERS[new_index]
        return new_index, new_param.replace("_", " ").title(), new_param

    
    # 📆 Switch date with arrows or calendar
    @dash_app.callback(
        Output('heatmap-date', 'value'),
        Output('heatmap-date-index', 'data'),
        Output('heatmap-date-picker', 'date'),
        Input('prev-heatmap-date', 'n_clicks'),
        Input('next-heatmap-date', 'n_clicks'),
        Input('heatmap-date-picker', 'date'),
        State('heatmap-date-index', 'data'),
        prevent_initial_call=True
    )
    def switch_or_select_heatmap_date(prev_clicks, next_clicks, selected_date, current_index):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update

        df = load_wifi_data()
        dates = sorted(pd.to_datetime(df['timestamp']).dt.date.unique())

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if triggered_id == 'prev-heatmap-date':
            new_index = (current_index - 1) % len(dates)
            new_date = str(dates[new_index])
        elif triggered_id == 'next-heatmap-date':
            new_index = (current_index + 1) % len(dates)
            new_date = str(dates[new_index])
        elif triggered_id == 'heatmap-date-picker':
            picked_date = pd.to_datetime(selected_date).date()
            if picked_date in dates:
                new_index = dates.index(picked_date)
                new_date = str(picked_date)
            else:
                return dash.no_update, dash.no_update, dash.no_update
        else:
            return dash.no_update, dash.no_update, dash.no_update

        return new_date, new_index, new_date

    
    # 🔁 Switch run using ◀️ ▶️ buttons or reset on date change
    @dash_app.callback(
        Output('heatmap-run-index', 'data'),
        Output('current-heatmap-run-display', 'children'),
        Output('heatmap-run', 'value'),
        Input('prev-heatmap-run', 'n_clicks'),
        Input('next-heatmap-run', 'n_clicks'),
        Input('heatmap-date', 'value'),
        State('heatmap-run-index', 'data'),
        prevent_initial_call=True
    )
    def switch_or_reset_heatmap_run(prev_clicks, next_clicks, selected_date, current_index):
        ctx = dash.callback_context
        if not selected_date:
            return current_index, dash.no_update, dash.no_update

        df = load_wifi_data()
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        selected_date_obj = pd.to_datetime(selected_date).date()
        run_list = sorted(df[df['date'] == selected_date_obj]['run_no'].unique())

        if not run_list:
            return 0, "No runs", ''

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if triggered_id == 'prev-heatmap-run':
            new_index = (current_index - 1) % len(run_list)
        elif triggered_id == 'next-heatmap-run':
            new_index = (current_index + 1) % len(run_list)
        else:
            new_index = 0  # reset to first run on date change

        new_run = str(run_list[new_index])
        return new_index, f"Run {new_run}", new_run


    # 🗺️ Generate heatmap based on selected param/date/run
    @dash_app.callback(
        Output('heatmap-graph', 'figure'),
        Input('heatmap-param', 'value'),
        Input('heatmap-date', 'value'),
        Input('heatmap-run', 'value')
    )
    def render_heatmap(param, selected_date, selected_run):
        df = load_wifi_data()
        if df.empty or not selected_date or not selected_run:
            return go.Figure()

        # Filter data by selected date and run
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        df = df[(df['date'] == pd.to_datetime(selected_date).date()) & 
                (df['run_no'] == int(selected_run))]

        # Aggregate data by location and selected parameter
        agg_df = df.groupby('location').agg({
            **{param: 'mean' for param in PARAMETERS},  # Use the PARAMETERS list dynamically
            'timestamp': 'count'
        }).reset_index().rename(columns={'timestamp': 'count'})

        if param not in agg_df.columns:
            return go.Figure()  # Return an empty figure if the selected param doesn't exist

        # Map locations to pixel coordinates
        agg_df['x'], agg_df['y'] = zip(*agg_df['location'].map(get_pixel_coords))
        agg_df = agg_df.dropna(subset=[param, 'x', 'y'])
        agg_df = agg_df[(agg_df['x'] != 0) | (agg_df['y'] != 0)]  # Remove unmapped (0,0)

        # Normalize marker size
        max_count = agg_df['count'].max()
        agg_df['size'] = agg_df['count'] / max_count * 40 + 10  # Marker size scale

        # 🛠️ Prepare hover template dynamically based on available params
        available_params = [p for p in PARAMETERS if p in agg_df.columns]
        customdata = agg_df[['location'] + available_params + ['count']]

        hover_lines = ["<b>%{customdata[0]}</b><br>"]  # Location
        for idx, p in enumerate(available_params, start=1):
            hover_lines.append(f"{p.replace('_', ' ').title()}: "+"%{customdata["+str(idx)+"]:.2f}<br>")
        hover_lines.append("Data Points: %{customdata["+str(len(available_params)+1)+"]}<extra></extra>")
        hovertemplate = ''.join(hover_lines)

        # Create the scatter plot
        fig = go.Figure(data=go.Scatter(
            x=agg_df['x'],
            y=agg_df['y'],
            mode='markers',
            marker=dict(
                size=agg_df['size'],
                color=agg_df[param],
                colorscale=[  # Replace this line
                    [0.0, "red"],
                    [0.5, "yellow"],
                    [1.0, "green"]
                ],
                showscale=True,
                line=dict(width=1, color='black'),
                colorbar=dict(
                    title=dict(text=param.replace('_', ' ').title(), side='right'),
                    len=1,
                    thickness=20,
                    xpad=10,
                    tickformat="0.1f"
                )
            ),
            customdata=customdata,
            hovertemplate=hovertemplate
        ))

        fig.update_layout(
            title=f"📍{param.replace('_', ' ').title()} Across Locations",
            xaxis=dict(
                 title="X",
                 showgrid=False,
                 zeroline=False,
                 range=[0, 1250],
                 constrain='domain',  # Lock the x-range width
                 tickmode='linear',
                 tick0=0,
                 dtick=50,  # Control spacing between ticks
             ),
             yaxis=dict(
                 title="Y",
                 showgrid=False,
                 zeroline=False,
                 range=[0, 350],
                 scaleanchor="x",     # Equal spacing per unit
                 tickmode='linear',
                 tick0=0,
                 dtick=50,
             ),
            plot_bgcolor='white',
            height=400,
            margin=dict(l=60, r=100, t=50, b=50)
        )


        
        return fig
