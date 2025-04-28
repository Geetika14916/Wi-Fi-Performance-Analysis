# modules/callbacks/trends_callbacks.py
import pandas as pd
import dash
import plotly.express as px
from dash import Input, Output, State, dcc, html
import plotly.graph_objects as go
from modules.data_loader import load_wifi_data
from modules.config import PARAMETER_LABELS, PARAMETERS

def register_trends_callbacks(dash_app, colors):
    # ════════════════════════════════════════════════════════════════
    # SECTION: TRENDS TAB CALLBACKS
    # Generates time series and hourly bar charts for selected location/parameters
    # ════════════════════════════════════════════════════════════════

    # 🔁 Change current location with prev/next buttons
    @dash_app.callback(
        Output('location-index', 'data'),
        Output('current-location-display', 'children'),
        Output('trends-location', 'value'),
        Input('prev-location-btn', 'n_clicks'),
        Input('next-location-btn', 'n_clicks'),
        State('location-index', 'data'),
        prevent_initial_call=True
    )
    def switch_trends_location(prev_clicks, next_clicks, current_index):
        ctx = dash.callback_context if hasattr(dash, 'callback_context') else dash.ctx
        if not ctx.triggered:
            return current_index, dash.no_update, dash.no_update

        df = load_wifi_data()
        locations = sorted(df['location'].unique())

        if not locations:
            return 0, "No locations", None

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if triggered_id == 'prev-location-btn':
            new_index = (current_index - 1) % len(locations)
        else:
            new_index = (current_index + 1) % len(locations)

        new_location = locations[new_index]
        return new_index, new_location, new_location


    # 📊 Update trends time series chart based on selected location, parameters, and date range
    @dash_app.callback(
        Output('trends-time-series', 'figure'),
        Input('trends-location', 'value'),
        Input('trends-parameters', 'value'),
        Input('trends-date-range', 'start_date'),
        Input('trends-date-range', 'end_date')
    )
    def render_trend_time_series_chart(location, parameters, start_date, end_date, colors=colors):
        df = load_wifi_data()
        if df.empty or not location or not parameters:
            return go.Figure()

        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        df['run_label'] = df.apply(lambda row: f"{row['date']} | Run {row['run_no']}", axis=1)

        filtered_df = df[df['location'] == location]

        # Filter date range dynamically
        if start_date and end_date:
            start = pd.to_datetime(start_date).date()
            end = pd.to_datetime(end_date).date()
            filtered_df = filtered_df[(filtered_df['date'] >= start) & (filtered_df['date'] <= end)]

        # Ensure full run label range exists (to fill missing runs)
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        run_label_df = df[['run_label', 'date']].drop_duplicates()
        if start_date and end_date:
            run_label_df = run_label_df[(run_label_df['date'] >= start) & (run_label_df['date'] <= end)]

        all_runs = run_label_df[['run_label']].sort_values('run_label')
        if all_runs.empty:
            return go.Figure()

        fig = go.Figure()

        for param in parameters:
            # Fetch min and max dynamically
            global_min = df[param].min()
            global_max = df[param].max()
            if global_min == global_max:
                global_min -= 1
                global_max += 1

            # Compute average per run and merge with all possible run labels
            param_avg = filtered_df[['run_label', param]].groupby('run_label').mean().reset_index()
            merged = all_runs.merge(param_avg, on='run_label', how='left')

            # Normalize and label
            merged['normalized'] = merged[param].apply(
                lambda x: (x - global_min) / (global_max - global_min) if pd.notna(x) else None
            )
            merged['normalized'] = merged['normalized'].fillna(0.0001).replace(0, 0.0001)
            merged.loc[merged[param] == 0, 'normalized'] = 0.0001

            unit = PARAMETER_LABELS[param].split()[-1].strip("()")
            merged['label'] = merged[param].apply(
                lambda x: f"{x:.2f} {unit}" if pd.notna(x) else "<br>No<br>Data"
            )

            # Dynamically handle colors
            fig.add_trace(go.Bar(
                x=merged['run_label'],
                y=merged['normalized'],
                name=PARAMETER_LABELS[param],
                text=merged['label'],
                textposition='auto',
                hovertemplate=(f"<b>{PARAMETER_LABELS[param]}</b><br>" +
                               "Run: %{x}<br>" +
                               "Normalized: %{y:.2f}<br>" +
                               "Value: %{text}<extra></extra>"),
                marker=dict(
                    color=colors.get(param, 'gray'),
                    line=dict(color=colors.get(param, 'gray'), width=2)
                )
            ))

        fig.update_layout(
            title=f"Normalized Parameter Comparison - {location}",
            barmode='group',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color=colors.get('text', 'black')),
            margin=dict(l=60, r=20, t=50, b=50),
            xaxis=dict(tickangle=-45),
            yaxis=dict(range=[0, 1], visible=False),
            showlegend=True
        )

        return fig


    # ⏱ Shift the trends date range using ◀️ ▶️ buttons
    @dash_app.callback(
        Output('trends-date-range', 'start_date'),
        Output('trends-date-range', 'end_date'),
        Output('trends-date-index', 'data'),
        Input('prev-trends-date', 'n_clicks'),
        Input('next-trends-date', 'n_clicks'),
        State('trends-date-range', 'start_date'),
        State('trends-date-range', 'end_date'),
        State('trends-date-index', 'data'),
        prevent_initial_call=True
    )
    def shift_trends_date_range(prev_clicks, next_clicks, start_date, end_date, current_index):
        ctx = dash.callback_context
        if not ctx.triggered or not start_date or not end_date:
            return dash.no_update, dash.no_update, dash.no_update

        df = load_wifi_data()
        available_dates = sorted(pd.to_datetime(df['timestamp']).dt.date.unique())
        if not available_dates:
            return dash.no_update, dash.no_update, dash.no_update

        start = pd.to_datetime(start_date).date()
        end = pd.to_datetime(end_date).date()

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if triggered_id == 'prev-trends-date':
            new_start = start - pd.Timedelta(days=1)
            new_end = end
        else:
            new_start = start
            new_end = end + pd.Timedelta(days=1)

        new_start = max(new_start, available_dates[0])
        new_end = min(new_end, available_dates[-1])

        if new_end < new_start:
            new_end = new_start
        if new_start > new_end:
            new_start = new_end

        return str(new_start), str(new_end), current_index


    # 📊 (Optional) Render hourly bar chart when 'All Hours' selected
    @dash_app.callback(
        Output('hourly-bar-wrapper', 'children'),
        Input('trends-location', 'value'),
        Input('trends-parameters', 'value'),
        Input('trends-hour', 'value')
    )
    def render_hourly_avg_chart(location, parameter, selected_hour):
        df = load_wifi_data()
        if df.empty or not location or selected_hour != 'All Hours':
            return None  # Hide container

        filtered = df[df['location'] == location]
        hourly_avg = filtered.groupby('hour')[parameter].mean().reset_index()

        fig = px.bar(
            hourly_avg,
            x='hour',
            y=parameter,
            title=f"Hourly Average of {parameter.replace('_', ' ').title()} - {location}",
            color=parameter,
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color=colors['text'], size=14),
            margin=dict(l=60, r=20, t=50, b=50),
            height=400
        )

        return html.Div([dcc.Graph(figure=fig, className='graph-container')])
