# modules/callbacks/heatmap_callbacks.py
import dash
from dash import Input, Output,State
import plotly.express as px
from modules.data_loader import load_wifi_data, prepare_heatmap_data
from modules.config import PARAMETERS
import pandas as pd
import plotly.graph_objects as go
from modules.utils import get_pixel_coords

def register_heatmap_callbacks(dash_app, colors):

    # ════════════════════════════════════════════════════════════════
    # SECTION: HEATMAP TAB CALLBACKS
    # Handles parameter/date/run switching and heatmap generation
    # ════════════════════════════════════════════════════════════════

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

        # Filter data
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        df = df[(df['date'] == pd.to_datetime(selected_date).date()) & 
                (df['run_no'] == int(selected_run))]

        # Aggregate per location
        agg_df = df.groupby('location').agg({
            'download_speed': 'mean',
            'upload_speed': 'mean',
            'latency_ms': 'mean',
            'jitter_ms': 'mean',
            'packet_loss': 'mean',
            'rssi': 'mean',
            'timestamp': 'count'
        }).reset_index().rename(columns={'timestamp': 'count'})

        # Map locations to pixel coordinates
        agg_df['x'], agg_df['y'] = zip(*agg_df['location'].map(get_pixel_coords))
        agg_df = agg_df.dropna(subset=[param, 'x', 'y'])
        agg_df = agg_df[(agg_df['x'] != 0) | (agg_df['y'] != 0)]  # filter unmapped (0,0)

        # Normalize marker size
        max_count = agg_df['count'].max()
        agg_df['size'] = agg_df['count'] / max_count * 40 + 10  # size scale: 10–50 px

        fig = go.Figure(data=go.Scatter(
            x=agg_df['x'],
            y=agg_df['y'],
            mode='markers',
            marker=dict(
                size=agg_df['size'],
                color=agg_df[param],
                colorscale='Viridis',
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
            customdata=agg_df[['location'] + PARAMETERS + ['count']],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>" +
                "Download: %{customdata[1]:.2f} Mbps<br>" +
                "Upload: %{customdata[2]:.2f} Mbps<br>" +
                "Latency: %{customdata[3]:.2f} ms<br>" +
                "Jitter: %{customdata[4]:.2f} ms<br>" +
                "Packet Loss: %{customdata[5]}<br>" +
                "RSSI: %{customdata[6]}<br>" +
                "Data Points: %{customdata[7]}<extra></extra>"
            )
        ))

        fig.update_layout(
            title=f"📍{param.replace('_', ' ').title()} Across Locations",
            xaxis=dict(title="X", showgrid=False, zeroline=False, range=[0, 550]),
            yaxis=dict(title="Y", showgrid=False, zeroline=False, range=[0, 350]),
            plot_bgcolor='white',
            height=400,
            margin=dict(l=60, r=100, t=50, b=50)
        )

        return fig

