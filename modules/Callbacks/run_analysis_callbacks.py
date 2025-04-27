# modules/callbacks/run_analysis_callbacks.py

from dash import Input, Output, State, dcc, html
from modules.data_loader import load_wifi_data
from modules.config import PARAMETER_LABELS, PARAMETERS
import plotly.graph_objects as go
import pandas as pd

def register_run_analysis_callbacks(dash_app, colors):

    @dash_app.callback(
        Output('location-plots', 'children'),
        Input('location-plot-selector', 'value'),
        Input('date-plot-selector', 'date'),
        Input('run-plot-selector', 'value')
    )
    def render_location_wise_comparison_graphs(selected_location, selected_date, selected_run):
        df = load_wifi_data()
        if df.empty or not selected_location or not selected_date or not selected_run:
            return html.Div("No data available for selected parameters", style={
                'color': 'white',
                'backgroundColor': '#1f2c3e',
                'padding': '20px',
                'borderRadius': '10px',
                'textAlign': 'center',
                'margin': '20px 0'
            })

        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        selected_date_obj = pd.to_datetime(selected_date).date()
        run_data = df[(df['date'] == selected_date_obj) & 
                    (df['run_no'] == int(selected_run)) &
                    (df['location'] == selected_location)]

        if len(run_data) == 0:
            return html.Div("No records found for selected date and run", style={
                'color': 'white',
                'backgroundColor': '#1f2c3e',
                'padding': '20px',
                'borderRadius': '10px',
                'textAlign': 'center',
                'margin': '20px 0'
            })

        time_str = run_data['timestamp'].iloc[0].strftime('%H:%M:%S')

        fig = go.Figure()
        for param in PARAMETERS:
            fig.add_trace(go.Bar(
                name=PARAMETER_LABELS[param],
                x=[param],
                y=[run_data[param].iloc[0]],
                marker_color=colors.get(param, 'gray'),
                text=[f"{run_data[param].iloc[0]:.2f}{PARAMETER_LABELS[param].split('(')[1].strip(')')}"],
                textposition='auto',
                hovertemplate=f"<b>{PARAMETER_LABELS[param]}</b><br>Value: %{{y:.2f}}<br>Time: {time_str}<extra></extra>"
            ))

        fig.update_layout(
            title=dict(
                text=f"Parameters for {selected_location}<br><sup>Date: {selected_date} | Time: {time_str} | Run: {selected_run}</sup>",
                x=0.5, xanchor='center', yanchor='top'
            ),
            barmode='group',
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color=colors['text']),
            margin=dict(l=60, r=20, t=80, b=50),
            height=400,
            yaxis=dict(visible=False)  # Hide y-axis
        )

        return html.Div([
            html.H4(selected_location, style={
                'color': 'white', 'marginBottom': '20px', 'textAlign': 'center',
                'backgroundColor': '#1f2c3e', 'padding': '10px', 'borderRadius': '10px'
            }),
            dcc.Graph(figure=fig)
        ])

