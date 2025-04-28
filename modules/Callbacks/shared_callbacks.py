import dash
import pandas as pd
from dash import Input, Output, State
from modules.data_loader import load_wifi_data

def register_shared_callbacks(dash_app, colors):
    # ════════════════════════════════════════════════════════════════
    # SECTION: SHARED CALLBACKS & INTERACTIONS
    # Toggle buttons, state management, and shared data navigation
    # ════════════════════════════════════════════════════════════════

    # 🔘 Open data collection page (via hidden link trigger)
    dash_app.clientside_callback(
        """
        function(n_clicks) {
            if (n_clicks > 0) {
                const link = document.getElementById('hidden-link');
                if (link) link.click();
            }
            return '';
        }
        """,
        Output('hidden-link', 'data-dummy'),
        Input('data-toggle-btn', 'n_clicks')
    )

    # 🔁 Switch location (prev/next) in Overview
    @dash_app.callback(
        Output('location-card-index', 'data'),
        Output('location-selector', 'value'),
        Input('prev-location-card', 'n_clicks'),
        Input('next-location-card', 'n_clicks'),
        State('location-card-index', 'data'),
        prevent_initial_call=True
    )
    def switch_overview_location(prev_clicks, next_clicks, current_index):
        ctx = dash.callback_context
        if not ctx.triggered:
            return current_index, dash.no_update

        df = load_wifi_data()
        locations = sorted(df['location'].unique())

        if not locations:
            return 0, None

        triggered_id = ctx.triggered_id
        if triggered_id == 'prev-location-card':
            new_index = (current_index - 1) % len(locations)
        else:
            new_index = (current_index + 1) % len(locations)

        return new_index, locations[new_index]

    # 🔁 Switch date (prev/next) in Run Analysis
    @dash_app.callback(
        Output('date-plot-index', 'data'),
        Output('date-plot-selector', 'date'),
        Input('prev-date-plot', 'n_clicks'),
        Input('next-date-plot', 'n_clicks'),
        Input('date-plot-selector', 'date'),
        State('date-plot-index', 'data'),
        prevent_initial_call=True
    )
    def switch_run_analysis_date(prev_clicks, next_clicks, selected_date, current_index):
        ctx = dash.callback_context
        if not ctx.triggered:
            return current_index, dash.no_update

        df = load_wifi_data()
        dates = sorted(pd.to_datetime(df['timestamp']).dt.date.unique())

        if not dates:
            return 0, None

        triggered_id = ctx.triggered_id
        if triggered_id in ['prev-date-plot', 'next-date-plot']:
            delta = -1 if triggered_id == 'prev-date-plot' else 1
            new_index = (current_index + delta) % len(dates)
            return new_index, dates[new_index]

        if triggered_id == 'date-plot-selector':
            picked_date = pd.to_datetime(selected_date).date()
            if picked_date in dates:
                return dates.index(picked_date), picked_date

        return current_index, dash.no_update

    # 🔁 Switch run (prev/next) in Run Analysis
    @dash_app.callback(
        Output('run-plot-index', 'data'),
        Output('run-plot-selector', 'value'),
        Input('prev-run-plot', 'n_clicks'),
        Input('next-run-plot', 'n_clicks'),
        Input('date-plot-selector', 'value'),
        State('run-plot-index', 'data'),
        prevent_initial_call=True
    )
    def switch_run_analysis_run(prev_clicks, next_clicks, selected_date, current_index):
        ctx = dash.callback_context
        if not selected_date:
            return current_index, dash.no_update

        df = load_wifi_data()
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        selected_date_obj = pd.to_datetime(selected_date).date()
        run_list = sorted(df[df['date'] == selected_date_obj]['run_no'].unique())

        if not run_list:
            return 0, None

        triggered_id = ctx.triggered_id
        if triggered_id in ['prev-run-plot', 'next-run-plot']:
            delta = -1 if triggered_id == 'prev-run-plot' else 1
            new_index = (current_index + delta) % len(run_list)
        else:
            new_index = 0  # On new date selection, default to first run

        return new_index, str(run_list[new_index])

    # 🔁 Switch location (prev/next) in Run Analysis
    @dash_app.callback(
        Output('location-plot-index', 'data'),
        Output('location-plot-selector', 'value'),
        Input('prev-location-plot', 'n_clicks'),
        Input('next-location-plot', 'n_clicks'),
        State('location-plot-index', 'data'),
        State('location-plot-selector', 'value'),
        prevent_initial_call=True
    )
    def switch_run_analysis_location(prev_clicks, next_clicks, current_index, current_location):
        ctx = dash.callback_context
        if not ctx.triggered:
            return current_index, dash.no_update

        df = load_wifi_data()
        locations = sorted(df['location'].unique())

        if not locations:
            return 0, None

        # If current location exists, sync current index
        if current_location in locations:
            current_index = locations.index(current_location)

        triggered_id = ctx.triggered_id
        if triggered_id == 'prev-location-plot':
            new_index = (current_index - 1) % len(locations)
        else:
            new_index = (current_index + 1) % len(locations)

        return new_index, locations[new_index]
