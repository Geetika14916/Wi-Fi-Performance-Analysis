import dash
from dash import Input, Output, State, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go

from modules.data_loader import load_wifi_data
from modules.config import PARAMETER_LABELS, PARAMETERS

def register_overview_callbacks(dash_app, colors):
    # ════════════════════════════════════════════════════════════════
    # SECTION: OVERVIEW TAB CALLBACKS
    # Displays parameter cards and run-by-location options
    # ════════════════════════════════════════════════════════════════

    # 📊 Generate cards showing latest parameter values for selected location
    @dash_app.callback(
        Output('parameter-cards', 'children'),
        Input('location-selector', 'value')
    )
    def render_parameter_cards(location):
        df = load_wifi_data()
        if df.empty or not location:
            return html.Div()

        latest_record = df[df['location'] == location].sort_values('timestamp').iloc[-1]

        parameter_info = {
            'download_speed': {'icon': '📥', 'unit': 'Mbps', 'label': 'Download Speed'},
            'upload_speed': {'icon': '📤', 'unit': 'Mbps', 'label': 'Upload Speed'},
            'latency_ms': {'icon': '⏱️', 'unit': 'ms', 'label': 'Latency'},
            'jitter_ms': {'icon': '📊', 'unit': 'ms', 'label': 'Jitter'},
            'packet_loss': {'icon': '📉', 'unit': '%', 'label': 'Packet Loss'},
            'rssi': {'icon': '📶', 'unit': 'dBm', 'label': 'RSSI'}
        }

        cards = []
        for param, meta in parameter_info.items():
            value = latest_record.get(param, None)
            if value is None:
                continue

            cards.append(
                dbc.Card(
                    dbc.CardBody([
                        html.Div(meta['icon'], style={
                            'fontSize': '3rem', 'display': 'flex', 'justifyContent': 'center',
                            'alignItems': 'center', 'height': '80px'
                        }),
                        html.H5(meta['label'], style={
                            'textAlign': 'center', 'color': 'white', 'marginTop': '10px',
                            'fontWeight': 'bold'
                        }),
                        html.H4(f"{value:.2f} {meta['unit']}", style={
                            'textAlign': 'center', 'marginTop': '5px', 'color': 'white'
                        })
                    ]),
                    style={
                        'height': '200px', 'margin': '10px', 'backgroundColor': '#1f2c3e',
                        'borderRadius': '15px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.3)',
                        'flex': '1', 'minWidth': '150px'
                    }
                )
            )

        return html.Div(cards, style={
            'display': 'flex', 'gap': '10px', 'flexWrap': 'nowrap', 'overflowX': 'auto'
        })

    # 🔄 Update run dropdown options based on selected date
    @dash_app.callback(
        Output('run-selector', 'options'),
        Input('date-selector', 'value')
    )
    def update_run_options(selected_date):
        df = load_wifi_data()
        if df.empty or not selected_date:
            return []

        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        runs = sorted(df[df['date'] == pd.to_datetime(selected_date).date()]['run_no'].unique())
        return [{'label': f"Run {run}", 'value': str(run)} for run in runs]

    # 🧠 Automatically select first available run if options update
    @dash_app.callback(
        Output('run-selector', 'value'),
        Input('run-selector', 'options')
    )
    def auto_select_first_run(options):
        if not options:
            return None
        return options[0]['value']
