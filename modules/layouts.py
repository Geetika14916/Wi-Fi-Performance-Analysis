from dash import html, dcc
import pandas as pd
import dash_bootstrap_components as dbc
from modules.config import PARAMETERS, PARAMETER_LABELS


def serve_layout(colors, locations, dates, hours):
    return html.Div([
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='collection-state', data={'active': False}),


        # 📍 Top-right Start/Stop Button
    html.Div([
        html.Div([
            html.Button("Collection", id='data-toggle-btn', n_clicks=0, className='small-btn'),
            html.A(id='hidden-link', href='/collection', target='_blank', style={'display': 'none'})
        ], style={
            'position': 'absolute',
            'top': '15px',
            'right': '30px',
            'zIndex': 999
        })
    ]),

        # 🧭 Page Header and Tabs Section
        html.Div([
            html.H2("Airport WiFi Performance", style={
                'margin': '0',
                'padding': '20px 0 30px 0',
                'textAlign': 'center',
                'color': colors['text']
            }),

            # Styled Tabs
            dcc.Tabs(
                id='main-tabs',
                value='overview',
                children=[
                    dcc.Tab(label='Overview', value='overview', className='custom-tab', selected_className='custom-tab-selected'),
                    dcc.Tab(label='Run Analysis', value='run_analysis', className='custom-tab', selected_className='custom-tab-selected'),
                    dcc.Tab(label='Trends', value='trends', className='custom-tab', selected_className='custom-tab-selected'),
                    dcc.Tab(label='Heatmap', value='heatmap', className='custom-tab', selected_className='custom-tab-selected'),
                    dcc.Tab(label='Insights', value='insights', className='custom-tab', selected_className='custom-tab-selected'),
                ],
                className='custom-tabs',
                style={'marginBottom': '0'}
            )
        ], style={
            'maxWidth': '1400px',
            'margin': '0 auto',
            'padding': '20px'
        }),

        # 📦 Main Content Area (varies by tab)
        html.Div(id='tab-content', style={
            'padding': '30px',
            'backgroundColor': colors['background'],
            'minHeight': 'calc(100vh - 150px)',
            'maxWidth': '1400px',
            'margin': '0 auto'
        })
    ])

def overview_layout(df):
    if df.empty:
        return html.Div("❌ No data available for overview")

    # Get latest run for each location
    latest_data = df.sort_values('timestamp').groupby('location').last().reset_index()
    
    # Define parameters to show
    parameters = {
        'download_speed': {'icon': '📥', 'unit': 'Mbps', 'name': 'Download Speed'},
        'upload_speed': {'icon': '📤', 'unit': 'Mbps', 'name': 'Upload Speed'},
        'latency_ms': {'icon': '⏱️', 'unit': 'ms', 'name': 'Latency'},
        'jitter_ms': {'icon': '📊', 'unit': 'ms', 'name': 'Jitter'},
        'packet_loss': {'icon': '📉', 'unit': '%', 'name': 'Packet Loss'},
        'rssi': {'icon': '📶', 'unit': 'dBm', 'name': 'RSSI'}
    }

    # Get unique locations for dropdown
    locations = latest_data['location'].unique()
    location_options = [{'label': loc, 'value': loc} for loc in locations]

    return html.Div([
        html.H3("📊 Latest Parameters", style={'marginBottom': '20px', 'color': 'white'}),
        html.Div([
            html.Label("Select Location:", style={'color': 'white', 'marginRight': '15px', 'minWidth': '100px'}),
            dbc.Button("⬅", id='prev-location-card', 
                        style={
                            'backgroundColor': '#1f2c3e',
                            'borderColor': '#1f2c3e',
                            'color': 'white',
                            'padding': '0.375rem 0.75rem',
                            'height': '38px',
                            'width': '45px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'marginRight': '8px',
                            'borderRadius': '4px',
                            'fontSize': '20px'
                        }),
            dcc.Dropdown(
                id='location-selector',
                options=location_options,
                value=locations[0] if len(locations) > 0 else None,
                clearable=False,
                style={
                    'width': '200px',
                    'backgroundColor': 'white',
                    'color': 'black',
                    'border': '1px solid #1f2c3e',
                    'borderRadius': '4px'
                }
            ),
            dbc.Button("➡", id='next-location-card',
                        style={
                            'backgroundColor': '#1f2c3e',
                            'borderColor': '#1f2c3e',
                            'color': 'white',
                            'padding': '0.375rem 0.75rem',
                            'height': '38px',
                            'width': '45px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'marginLeft': '8px',
                            'borderRadius': '4px',
                            'fontSize': '20px'
                        }),
            dcc.Store(id='location-card-index', data=0)
        ], style={'marginBottom': '20px', 'display': 'flex', 'alignItems': 'center'}),
        html.Div(id='parameter-cards', style={'marginTop': '30px'})
    ], style={'padding': '20px', 'backgroundColor': '#15202b', 'minHeight': '100vh'})

def run_analysis_layout(df):
    if df.empty:
        return html.Div("❌ No data available for run analysis")

    # Get unique locations for dropdown
    locations = sorted(df['location'].unique())
    location_options = [{'label': loc, 'value': loc} for loc in locations]

    # Get unique dates and run numbers
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    dates = sorted(df['date'].unique())
    
    # Get run numbers for the first date
    first_date_data = df[df['date'] == dates[0]]
    first_date_runs = sorted(first_date_data['run_no'].unique())
    run_options = [{'label': f"Run {run}", 'value': str(run)} for run in first_date_runs]

    return html.Div([
        html.H3("Run Analysis", style={'marginBottom': '20px', 'color': 'white'}),
        html.Div([
            # Location Navigation
            html.Div([
                html.Label("Location:", style={'color': 'white', 'marginRight': '15px', 'minWidth': '100px'}),
                dbc.Button("⬅", id='prev-location-plot',
                            style={
                                'backgroundColor': '#1f2c3e',
                                'borderColor': '#1f2c3e',
                                'color': 'white',
                                'padding': '0.375rem 0.75rem',
                                'height': '38px',
                                'width': '45px',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'marginRight': '8px',
                                'borderRadius': '4px',
                                'fontSize': '20px'
                            }),
                dcc.Dropdown(
                    id='location-plot-selector',
                    options=location_options,
                    value=locations[0] if len(locations) > 0 else None,
                    clearable=False,
                    style={
                        'width': '200px',
                        'backgroundColor': 'white',
                        'color': 'black',
                        'border': '1px solid #1f2c3e',
                        'borderRadius': '4px'
                    }
                ),
                dbc.Button("➡", id='next-location-plot',
                            style={
                                'backgroundColor': '#1f2c3e',
                                'borderColor': '#1f2c3e',
                                'color': 'white',
                                'padding': '0.375rem 0.75rem',
                                'height': '38px',
                                'width': '45px',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'marginLeft': '8px',
                                'borderRadius': '4px',
                                'fontSize': '20px'
                            }),
                dcc.Store(id='location-plot-index', data=0)
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),
            
            # Date Navigation
            html.Div([
                html.Label("Date:", style={'color': 'white', 'marginRight': '15px', 'minWidth': '100px'}),
                dbc.Button("⬅", id='prev-date-plot',
                            style={
                                'backgroundColor': '#1f2c3e',
                                'borderColor': '#1f2c3e',
                                'color': 'white',
                                'padding': '0.375rem 0.75rem',
                                'height': '38px',
                                'width': '45px',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'marginRight': '8px',
                                'borderRadius': '4px',
                                'fontSize': '20px'
                            }),
                dcc.DatePickerSingle(
                    id='date-plot-selector',
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
                dbc.Button("➡", id='next-date-plot',
                            style={
                                'backgroundColor': '#1f2c3e',
                                'borderColor': '#1f2c3e',
                                'color': 'white',
                                'padding': '0.375rem 0.75rem',
                                'height': '38px',
                                'width': '45px',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'marginLeft': '8px',
                                'borderRadius': '4px',
                                'fontSize': '20px'
                            }),
                dcc.Store(id='date-plot-index', data=0)
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),
            
            # Run Navigation
            html.Div([
                html.Label("Run:", style={'color': 'white', 'marginRight': '15px', 'minWidth': '100px'}),
                dbc.Button("⬅", id='prev-run-plot',
                            style={
                                'backgroundColor': '#1f2c3e',
                                'borderColor': '#1f2c3e',
                                'color': 'white',
                                'padding': '0.375rem 0.75rem',
                                'height': '38px',
                                'width': '45px',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'marginRight': '8px',
                                'borderRadius': '4px',
                                'fontSize': '20px'
                            }),
                dcc.Dropdown(
                    id='run-plot-selector',
                    options=run_options,
                    value=str(first_date_runs[0]) if len(first_date_runs) > 0 else None,
                    clearable=False,
                    style={
                        'width': '200px',
                        'backgroundColor': 'white',
                        'color': 'black',
                        'border': '1px solid #1f2c3e',
                        'borderRadius': '4px'
                    }
                ),
                
                dbc.Button("➡", id='next-run-plot',
                            style={
                                'backgroundColor': '#1f2c3e',
                                'borderColor': '#1f2c3e',
                                'color': 'white',
                                'padding': '0.375rem 0.75rem',
                                'height': '38px',
                                'width': '45px',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'marginLeft': '8px',
                                'borderRadius': '4px',
                                'fontSize': '20px'
                            }),
                dcc.Store(id='run-plot-index', data=0)
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'})
        ]),
        html.Div(id='location-plots')
    ], style={'padding': '20px', 'backgroundColor': '#15202b', 'minHeight': '100vh'})

def trends_layout(df):
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
                    dbc.Button("⬅", id='prev-location-btn', 
                        style={
                            'backgroundColor': '#1f2c3e',
                            'borderColor': '#1f2c3e',
                            'color': 'white',
                            'padding': '0.375rem 0.75rem',
                            'height': '38px',
                            'width': '45px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'marginRight': '8px',
                            'borderRadius': '4px',
                            'fontSize': '20px'
                        }),
                    html.Div(locations[0] if locations else '', id='current-location-display', style={
                        'padding': '0 15px', 'color': 'white', 'fontWeight': 'bold', 'display': 'inline-block'
                    }),
                    dbc.Button("➡", id='next-location-btn',
                        style={
                            'backgroundColor': '#1f2c3e',
                            'borderColor': '#1f2c3e',
                            'color': 'white',
                            'padding': '0.375rem 0.75rem',
                            'height': '38px',
                            'width': '45px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'marginLeft': '8px',
                            'borderRadius': '4px',
                            'fontSize': '20px'
                        }),
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
                        dbc.Button("⬅", id='prev-trends-date', 
                        style={
                            'backgroundColor': '#1f2c3e',
                            'borderColor': '#1f2c3e',
                            'color': 'white',
                            'padding': '0.375rem 0.75rem',
                            'height': '38px',
                            'width': '45px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'marginRight': '8px',
                            'borderRadius': '4px',
                            'fontSize': '20px'
                        }),
                    dcc.DatePickerRange(
                        id='trends-date-range',
                        display_format='YYYY-MM-DD',
                        style={'margin': '0 10px'}
                    ),
                    dbc.Button("➡", id='next-trends-date',
                        style={
                            'backgroundColor': '#1f2c3e',
                            'borderColor': '#1f2c3e',
                            'color': 'white',
                            'padding': '0.375rem 0.75rem',
                            'height': '38px',
                            'width': '45px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'marginLeft': '8px',
                            'borderRadius': '4px',
                            'fontSize': '20px'
                        }),
                    dcc.Store(id='trends-date-index', data=0)
                ], style={'display': 'flex', 'alignItems': 'center'})
            ], className='filter-item'),

        ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px', 'flexWrap': 'wrap'}),

        dcc.Graph(id='trends-time-series', className='graph-container'),
        html.Div(id='hourly-bar-wrapper')  # Shown conditionally
    ])

def heatmap_layout(df):
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
                        dbc.Button("⬅", id='prev-heatmap-param', 
                        style={
                            'backgroundColor': '#1f2c3e',
                            'borderColor': '#1f2c3e',
                            'color': 'white',
                            'padding': '0.375rem 0.75rem',
                            'height': '38px',
                            'width': '45px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'marginRight': '8px',
                            'borderRadius': '4px',
                            'fontSize': '20px'
                        }),
                    html.Div(PARAMETERS[0].replace("_", " ").title(), id='current-heatmap-param-display', style={
                        'padding': '0 15px', 'color': 'white', 'fontWeight': 'bold', 'display': 'inline-block'
                    }),
                    dbc.Button("➡", id='next-heatmap-param',
                        style={
                            'backgroundColor': '#1f2c3e',
                            'borderColor': '#1f2c3e',
                            'color': 'white',
                            'padding': '0.375rem 0.75rem',
                            'height': '38px',
                            'width': '45px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'marginLeft': '8px',
                            'borderRadius': '4px',
                            'fontSize': '20px'
                        }),
                    dcc.Store(id='heatmap-param-index', data=0),
                    dcc.Input(id='heatmap-param', type='hidden', value=PARAMETERS[0])
                ], style={'display': 'flex', 'alignItems': 'center'})
            ], className='filter-item'),

            # Date switcher
            html.Div([
                html.Div("Date", className='filter-label'),
                html.Div([
                        dbc.Button("⬅", id='prev-heatmap-date', 
                        style={
                            'backgroundColor': '#1f2c3e',
                            'borderColor': '#1f2c3e',
                            'color': 'white',
                            'padding': '0.375rem 0.75rem',
                            'height': '38px',
                            'width': '45px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'marginRight': '8px',
                            'borderRadius': '4px',
                            'fontSize': '20px'
                        }),
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
                    dbc.Button("➡", id='next-heatmap-date',
                        style={
                            'backgroundColor': '#1f2c3e',
                            'borderColor': '#1f2c3e',
                            'color': 'white',
                            'padding': '0.375rem 0.75rem',
                            'height': '38px',
                            'width': '45px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'marginLeft': '8px',
                            'borderRadius': '4px',
                            'fontSize': '20px'
                        }),
                    dcc.Store(id='heatmap-date-index', data=0),
                    dcc.Input(id='heatmap-date', type='hidden', value=str(dates[0]) if dates else '')
                ], style={'display': 'flex', 'alignItems': 'center'})
            ], className='filter-item'),

            # Run switcher
            html.Div([
                html.Div("Run", className='filter-label'),
                html.Div([
                        dbc.Button("⬅", id='prev-heatmap-run', 
                        style={
                            'backgroundColor': '#1f2c3e',
                            'borderColor': '#1f2c3e',
                            'color': 'white',
                            'padding': '0.375rem 0.75rem',
                            'height': '38px',
                            'width': '45px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'marginRight': '8px',
                            'borderRadius': '4px',
                            'fontSize': '20px'
                        }),
                    html.Div(
                        f"Run {first_date_runs[0]}" if first_date_runs else 'No Run',
                        id='current-heatmap-run-display',
                        style={
                            'padding': '0 15px', 'color': 'white', 'fontWeight': 'bold', 'display': 'inline-block'
                        }
                    ),
                    dbc.Button("➡", id='next-heatmap-run',
                        style={
                            'backgroundColor': '#1f2c3e',
                            'borderColor': '#1f2c3e',
                            'color': 'white',
                            'padding': '0.375rem 0.75rem',
                            'height': '38px',
                            'width': '45px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'marginLeft': '8px',
                            'borderRadius': '4px',
                            'fontSize': '20px'
                        }),
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



