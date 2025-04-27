from dash import Input, Output, State, dcc, html
import dash_bootstrap_components as dbc
import dash_bootstrap_components as dbc
from modules.data_loader import load_wifi_data
from modules.Callbacks.overview_callbacks import register_overview_callbacks
from modules.Callbacks.run_analysis_callbacks import register_run_analysis_callbacks
from modules.Callbacks.trends_callbacks import register_trends_callbacks
from modules.Callbacks.heatmap_callbacks import register_heatmap_callbacks
from modules.Callbacks.shared_callbacks import register_shared_callbacks

from modules.layouts import overview_layout, run_analysis_layout, trends_layout, heatmap_layout



def register_callbacks(dash_app, colors):

    @dash_app.callback(
        Output('tab-content', 'children'),
        Input('main-tabs', 'value')
    )
    def render_selected_tab_content(tab):
        df = load_wifi_data()

        if tab == 'overview':
            return overview_layout(df)
        elif tab == 'run_analysis':
            return run_analysis_layout(df)
        elif tab == 'trends':
            return trends_layout(df)
        elif tab == 'heatmap':
            return heatmap_layout(df)
        elif tab == 'insights':
            return html.Div([
                html.H3("🧠 AI-based insights will go here.")
            ])

        return html.Div("🚧 This section is under construction.")


    # Register modular callbacks
    register_overview_callbacks(dash_app, colors)
    register_run_analysis_callbacks(dash_app, colors)
    register_trends_callbacks(dash_app, colors)
    register_heatmap_callbacks(dash_app, colors)
    register_shared_callbacks(dash_app, colors)