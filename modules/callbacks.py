from dash import Input, Output, html, dcc
from modules.data_loader import load_wifi_data,prepare_heatmap_data
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from modules.utils import get_pixel_coords
import dash_bootstrap_components as dbc
from datetime import datetime
from plotly.subplots import make_subplots
import dash

# ════════════════════════════════════════════════════════════════
# CONSTANTS
# ════════════════════════════════════════════════════════════════

PARAMETER_LABELS = {
    'download_speed': 'Download Speed (Mbps)',
    'upload_speed': 'Upload Speed (Mbps)',
    'latency_ms': 'Latency (ms)',
    'jitter_ms': 'Jitter (ms)',
    'packet_loss': 'Packet Loss (%)',
    'rssi': 'RSSI (dBm)'
}

PARAMETERS = list(PARAMETER_LABELS.keys())

def register_callbacks(dash_app, colors):
    # ════════════════════════════════════════════════════════════════
    # SECTION: MAIN TAB CONTENT RENDERING
    # Handles switching between tabs like overview, trends, heatmap
    # and loads the appropriate layout content dynamically
    # ════════════════════════════════════════════════════════════════

    @dash_app.callback(
        Output('tab-content', 'children'),
        Input('main-tabs', 'value')
    )
    def render_selected_tab_content(tab):
        """
        Main tab switcher. Dynamically loads the content for the selected tab.
        Tabs: overview, trends, heatmap, insights
        """
        df = load_wifi_data()

        if tab == 'overview':
            if df.empty:
                return html.Div("❌ No data available for overview")

            # Get latest data per location
            latest_data = df.sort_values('timestamp').groupby('location').last().reset_index()

            # Prepare dropdown options for location and date-run selection
            locations = list(latest_data['location'].unique())
            location_options = [{'label': loc, 'value': loc} for loc in locations]

            df['date'] = pd.to_datetime(df['timestamp']).dt.date
            dates = sorted(df['date'].unique())
            date_options = [{'label': str(date), 'value': str(date)} for date in dates]

            first_date_data = df[df['date'] == dates[0]]
            first_date_runs = sorted(first_date_data['run_no'].unique())
            run_options = [{'label': f"Run {run}", 'value': str(run)} for run in first_date_runs]

            return html.Div([
                html.H3("📊 Latest Parameters", style={'marginBottom': '20px', 'color': 'white'}),

                # Location selector dropdown
                html.Div([
                    html.Label("Select Location:", style={'color': 'white', 'marginRight': '10px'}),
                    dcc.Dropdown(
                        id='location-selector',
                        options=location_options,
                        value=locations[0] if locations else None,
                        clearable=False,
                        style={'width': '200px', 'display': 'inline-block', 'marginRight': '20px'}
                    )
                ], style={'marginBottom': '20px', 'display': 'flex', 'alignItems': 'center'}),

                html.Div(id='parameter-cards', style={'marginTop': '30px'}),
                html.Hr(style={'borderColor': 'white', 'margin': '30px 0'}),

                html.H3("Run Analysis", style={'marginTop': '40px', 'marginBottom': '20px', 'color': 'white'}),

                # Date and run selectors
                html.Div([
                    html.Div([
                        html.Label("Select Date:", style={'color': 'white', 'marginRight': '10px'}),
                        dcc.Dropdown(
                            id='date-selector',
                            options=date_options,
                            value=str(dates[0]) if dates else None,
                            clearable=False,
                            style={'width': '200px', 'display': 'inline-block', 'marginRight': '20px'}
                        )
                    ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),

                    html.Div([
                        html.Label("Select Run:", style={'color': 'white', 'marginRight': '10px'}),
                        dcc.Dropdown(
                            id='run-selector',
                            options=run_options,
                            value=str(first_date_runs[0]) if first_date_runs else None,
                            clearable=False,
                            style={'width': '200px', 'display': 'inline-block', 'marginRight': '20px'}
                        )
                    ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'})
                ]),

                html.Div(id='location-plots')
            ], style={'padding': '20px'})

        elif tab == 'trends':
            if df.empty:
                return html.Div("❌ No data available for trends view")

            locations = sorted(df['location'].unique())
            hours = ['All Hours'] + sorted(df['hour'].unique())

            return html.Div([
                html.Div([
                    # Location selector with prev/next buttons
                    html.Div([
                        html.Div("Location", className='filter-label'),
                        html.Div([
                            dbc.Button("◀️", id='prev-location-btn', color='primary', outline=True, size='sm'),
                            html.Div(locations[0] if locations else '', id='current-location-display', style={
                                'padding': '0 15px', 'color': 'white', 'fontWeight': 'bold', 'display': 'inline-block'
                            }),
                            dbc.Button("▶️", id='next-location-btn', color='primary', outline=True, size='sm'),
                            dcc.Store(id='location-index', data=0, storage_type='session'),
                            dcc.Input(id='trends-location', type='hidden', value=locations[0] if locations else '', debounce=True)
                        ], style={'display': 'flex', 'alignItems': 'center'})
                    ], className='filter-item'),

                    # Parameter checklist
                    html.Div([
                        html.Div("Parameters", className='filter-label'),
                        dcc.Checklist(
                            id='trends-parameters',
                            options=[{'label': PARAMETER_LABELS[p], 'value': p} for p in PARAMETERS],
                            value=['download_speed'],  # default selected
                            inline=True,
                            inputStyle={'marginRight': '5px'},
                            style={'color': 'white'}
                        )
                    ], className='filter-item'),

                    # Date Range picker with arrows
                    html.Div([
                        html.Div("Date Range", className='filter-label'),
                        html.Div([
                            dbc.Button("◀️", id='prev-trends-date', color='secondary', outline=True, size='sm'),
                            dcc.DatePickerRange(
                                id='trends-date-range',
                                display_format='YYYY-MM-DD',
                                style={'margin': '0 10px'}
                            ),
                            dbc.Button("▶️", id='next-trends-date', color='secondary', outline=True, size='sm'),
                            dcc.Store(id='trends-date-index', data=0)
                        ], style={'display': 'flex', 'alignItems': 'center'})
                    ], className='filter-item'),

                ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px', 'flexWrap': 'wrap'}),

                dcc.Graph(id='trends-time-series', className='graph-container'),
                html.Div(id='hourly-bar-wrapper')  # Shown conditionally
            ])

        elif tab == 'heatmap':
            if df.empty:
                return html.Div("❌ No data available for heatmap view")

            df['date'] = pd.to_datetime(df['timestamp']).dt.date
            dates = sorted(df['date'].unique())
            first_date_data = df[df['date'] == dates[0]]
            first_date_runs = sorted(first_date_data['run_no'].unique())

            return html.Div([
                html.Div([
                    # Parameter switcher
                    html.Div([
                        html.Div("Parameter", className='filter-label'),
                        html.Div([
                            dbc.Button("◀️", id='prev-heatmap-param', color='primary', outline=True, size='sm'),
                            html.Div(PARAMETERS[0].replace("_", " ").title(), id='current-heatmap-param-display', style={
                                'padding': '0 15px', 'color': 'white', 'fontWeight': 'bold', 'display': 'inline-block'
                            }),
                            dbc.Button("▶️", id='next-heatmap-param', color='primary', outline=True, size='sm'),
                            dcc.Store(id='heatmap-param-index', data=0),
                            dcc.Input(id='heatmap-param', type='hidden', value=PARAMETERS[0])
                        ], style={'display': 'flex', 'alignItems': 'center'})
                    ], className='filter-item'),

                    # Date switcher
                    html.Div([
                        html.Div("Date", className='filter-label'),
                        html.Div([
                            dbc.Button("◀️", id='prev-heatmap-date', color='secondary', outline=True, size='sm'),
                            dcc.DatePickerSingle(
                                id='heatmap-date-picker',
                                date=dates[0],
                                display_format='YYYY-MM-DD',
                                style={
                                    'backgroundColor': '#1f2c3e', 'color': 'white', 'border': '1px solid #ccc',
                                    'borderRadius': '5px', 'padding': '5px 10px', 'margin': '0 10px',
                                    'textAlign': 'center', 'fontWeight': 'bold', 'cursor': 'pointer'
                                },
                                className='custom-date-picker',
                                min_date_allowed=dates[0],
                                max_date_allowed=dates[-1],
                                disabled_days=[d for d in pd.date_range(start=dates[0], end=dates[-1]) if d.date() not in dates]
                            ),
                            dbc.Button("▶️", id='next-heatmap-date', color='secondary', outline=True, size='sm'),
                            dcc.Store(id='heatmap-date-index', data=0),
                            dcc.Input(id='heatmap-date', type='hidden', value=str(dates[0]) if dates else '')
                        ], style={'display': 'flex', 'alignItems': 'center'})
                    ], className='filter-item'),

                    # Run switcher
                    html.Div([
                        html.Div("Run", className='filter-label'),
                        html.Div([
                            dbc.Button("◀️", id='prev-heatmap-run', color='info', outline=True, size='sm'),
                            html.Div(
                                f"Run {first_date_runs[0]}" if first_date_runs else 'No Run',
                                id='current-heatmap-run-display',
                                style={
                                    'padding': '0 15px', 'color': 'white', 'fontWeight': 'bold', 'display': 'inline-block'
                                }
                            ),
                            dbc.Button("▶️", id='next-heatmap-run', color='info', outline=True, size='sm'),
                            dcc.Store(id='heatmap-run-index', data=0),
                            dcc.Input(id='heatmap-run', type='hidden', value=str(first_date_runs[0]) if first_date_runs else '')
                        ], style={'display': 'flex', 'alignItems': 'center'})
                    ], className='filter-item'),
                ], style={
                    'display': 'flex', 'gap': '300px', 'flexWrap': 'wrap',
                    'marginBottom': '20px', 'marginLeft': '70px'
                }),

                dcc.Graph(id='heatmap-graph', className='graph-container')
            ], style={'maxWidth': None, 'margin': '0 auto'})

        elif tab == 'insights':
            return html.Div([
                html.H3("🧠 AI-based insights will go here.")
            ])

        # Default fallback
        return html.Div("🚧 This section is under construction.")


    # ════════════════════════════════════════════════════════════════
    # SECTION: OVERVIEW TAB CALLBACKS
    # Includes parameter cards and run-by-location bar charts
    # ════════════════════════════════════════════════════════════════

    # 📊 Show cards with the latest parameter values for selected location
    @dash_app.callback(
        Output('parameter-cards', 'children'),
        Input('location-selector', 'value')
    )
    def render_latest_parameter_cards(selected_location):
        df = load_wifi_data()
        if df.empty or not selected_location:
            return html.Div()

        latest_data = df[df['location'] == selected_location].sort_values('timestamp').iloc[-1]

        parameter_meta = {
            'download_speed': {'icon': '📥', 'unit': 'Mbps', 'name': 'Download Speed'},
            'upload_speed': {'icon': '📤', 'unit': 'Mbps', 'name': 'Upload Speed'},
            'latency_ms': {'icon': '⏱️', 'unit': 'ms', 'name': 'Latency'},
            'jitter_ms': {'icon': '📊', 'unit': 'ms', 'name': 'Jitter'},
            'packet_loss': {'icon': '📉', 'unit': '%', 'name': 'Packet Loss'},
            'rssi': {'icon': '📶', 'unit': 'dBm', 'name': 'RSSI'}
        }

        cards = []
        for param, info in parameter_meta.items():
            cards.append(
                dbc.Card(
                    dbc.CardBody([
                        html.Div(info['icon'], style={
                            'fontSize': '3rem', 'textAlign': 'center', 'display': 'flex',
                            'justifyContent': 'center', 'alignItems': 'center', 'height': '80px'
                        }),
                        html.H5(info['name'], style={
                            'textAlign': 'center', 'color': 'white', 'marginTop': '10px', 'fontWeight': 'bold'
                        }),
                        html.H4(f"{latest_data[param]:.2f} {info['unit']}", style={
                            'textAlign': 'center', 'marginTop': '5px', 'color': 'white'
                        })
                    ]),
                    style={
                        'height': '200px', 'margin': '10px', 'backgroundColor': '#1f2c3e', 'color': 'white',
                        'borderRadius': '15px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.3)',
                        'flex': '1', 'minWidth': '0'
                    }
                )
            )

        return html.Div(
            cards,
            style={'display': 'flex', 'gap': '10px', 'flexWrap': 'nowrap', 'overflowX': 'auto'}
        )


    # 📉 Render stacked parameter bars for each location for selected date and run
    @dash_app.callback(
        Output('location-plots', 'children'),
        Input('date-selector', 'value'),
        Input('run-selector', 'value')
    )
    def render_location_wise_comparison_graphs(selected_date, selected_run):
        df = load_wifi_data()
        if df.empty or not selected_date or not selected_run:
            return html.Div()

        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        run_data = df[(df['date'] == pd.to_datetime(selected_date).date()) & 
                    (df['run_no'] == int(selected_run))]

        locations = run_data['location'].unique()
        if len(locations) == 0:
            return html.Div("No data available for selected date and run")

        plots = []
        for location in locations:
            loc_data = run_data[run_data['location'] == location]
            time_str = loc_data['timestamp'].iloc[0].strftime('%H:%M:%S')

            fig = go.Figure()
            for param in PARAMETERS:
                fig.add_trace(go.Bar(
                    name=PARAMETER_LABELS[param],
                    x=[param],
                    y=[loc_data[param].iloc[0]],
                    marker_color=colors.get(param, 'gray'),
                    text=[f"{loc_data[param].iloc[0]:.2f}"],
                    textposition='auto',
                    hovertemplate=f"<b>{PARAMETER_LABELS[param]}</b><br>Value: %{{y:.2f}}<br>Time: {time_str}<extra></extra>"
                ))

            fig.update_layout(
                title=dict(
                    text=f"Parameters for {location}<br><sup>Date: {selected_date} | Time: {time_str} | Run: {selected_run}</sup>",
                    x=0.5, xanchor='center', yanchor='top'
                ),
                barmode='group',
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color=colors['text']),
                margin=dict(l=60, r=20, t=80, b=50),
                height=400
            )

            plots.append(
                html.Div([
                    html.H4(location, style={
                        'color': 'white', 'marginBottom': '20px', 'textAlign': 'center',
                        'backgroundColor': '#1f2c3e', 'padding': '10px', 'borderRadius': '10px'
                    }),
                    dcc.Graph(figure=fig),
                    html.Hr(style={'borderColor': 'white', 'margin': '30px 0'})
                ])
            )

        return plots


    # 🔄 Update run dropdown options based on selected date
    @dash_app.callback(
        Output('run-selector', 'options'),
        Input('date-selector', 'value')
    )
    def load_run_dropdown_options(selected_date):
        df = load_wifi_data()
        if df.empty or not selected_date:
            return []

        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        runs = sorted(df[df['date'] == pd.to_datetime(selected_date).date()]['run_no'].unique())
        return [{'label': f"Run {run}", 'value': str(run)} for run in runs]


    # 🧠 Automatically select the first available run when run options change
    @dash_app.callback(
        Output('run-selector', 'value'),
        Input('run-selector', 'options')
    )
    def auto_select_first_run_value(options):
        if not options:
            return None
        return options[0]['value']


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

        # Filter date range
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
                lambda x: f"{x:.2f} {unit}" if pd.notna(x) else "NoData"
            )

            fig.add_trace(go.Bar(
                x=merged['run_label'],
                y=merged['normalized'],
                name=PARAMETER_LABELS[param],
                text=merged['label'],
                textposition='auto',
                hovertemplate=(
                    f"<b>{PARAMETER_LABELS[param]}</b><br>" +
                    "Run: %{x}<br>" +
                    "Normalized: %{y:.2f}<br>" +
                    "Value: %{text}<extra></extra>"
                ),
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

    # ════════════════════════════════════════════════════════════════
    # SECTION: INSIGHTS TAB (Coming Soon)
    # ════════════════════════════════════════════════════════════════

    # ════════════════════════════════════════════════════════════════
    # SECTION: SHARED CALLBACKS & INTERACTIONS
    # Toggle buttons, state management, and common data handlers
    # ════════════════════════════════════════════════════════════════

    # 🔘 Toggle data collection (start/stop) via button
    @dash_app.callback(
        Output('data-toggle-btn', 'children'),
        Output('collection-state', 'data'),
        Input('data-toggle-btn', 'n_clicks'),
        State('collection-state', 'data'),
        prevent_initial_call=True
    )
    def toggle_data_collection_state(n_clicks, state_data):
        """
        Toggles the data collection button label and state data.
        State is stored in dcc.Store as {'active': True/False}
        """
        if not state_data or 'active' not in state_data:
            state_data = {'active': False}

        new_state = not state_data['active']
        new_label = "Stop" if new_state else "Start"
        return new_label, {'active': new_state}