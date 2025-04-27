# modules/callbacks/overview_callbacks.py
import dash
from dash import Input, Output, State, dcc, html
import dash_bootstrap_components as dbc
from modules.data_loader import load_wifi_data
from modules.config import PARAMETER_LABELS, PARAMETERS
import pandas as pd
import plotly.graph_objects as go

def register_overview_callbacks(dash_app, colors):
    
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

