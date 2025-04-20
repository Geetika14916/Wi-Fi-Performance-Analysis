from dash import Dash
from modules.data_loader import load_wifi_data
from modules.layouts import serve_layout

from modules.callbacks import register_callbacks

def create_dash_app(flask_app):
    dash_app = Dash(__name__, server=flask_app, url_base_pathname='/dashboard/',suppress_callback_exceptions=True)

    colors = {
    'background': '#0F2027',       # dark teal/navy tone
    'navbar': '#1976D2',           # keep for brand blue accents
    'sidebar': '#1B2A41',          # muted dark background
    'text': '#1C2B36',             # soft light grey for text
    'primary': '#00BFA6',          # highlight/CTA (green-blue)
    'secondary': '#FFA000',        # warm contrast (amber)

    'download_speed': '#1f77b4',
    'upload_speed': '#ff7f0e',
    'latency_ms': '#2ca02c',
    'jitter_ms': '#d62728',
    'packet_loss': '#9467bd',
    'rssi': '#8c564b',
    # 'text': 'black'

}


    df = load_wifi_data()
    locations = sorted(df['location'].unique()) if not df.empty else []
    dates = ['All Dates'] + sorted(df['date'].unique()) if not df.empty else ['All Dates']
    hours = ['All Hours'] + sorted(df['hour'].unique()) if not df.empty else ['All Hours']

    dash_app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>WiFi Performance Analysis</title>
            {%favicon%}
            {%css%}
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
            <style>
body {
    margin: 0;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    background: #0F2027;
    color: #1C2B36;
}

h2, h3, h4 {
    font-weight: 600;
    color: #ECEFF1 !important;
}

.DatePickerSingle input {
    background-color: #1f2c3e !important;
    color: white !important;
    border: none;
    font-weight: bold;
    text-align: center;
}

.graph-container {
    background: #1B2A41;
    border-radius: 14px;
    padding: 20px;
    margin: 15px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease-in-out;
}

.graph-container:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.4);
}

.custom-tabs {
    border-bottom: 2px solid #33475B;
    margin-bottom: 10px;
}

.custom-tab {
    background: #263B5E;
    padding: 12px 25px;
    font-size: 16px;
    border: none;
    border-radius: 8px 8px 0 0;
    margin-right: 5px;
    color: #1C2B36;
    cursor: pointer;
    font-weight: 500;

}

.custom-tab:hover {
    background-color: #34495E;
    color: #ECEFF1;
}

.custom-tab-selected {
    background: #1B2A41 !important;
    border-bottom: 2px solid #1B2A41 !important;
    font-weight: 600;
    color: #00BFA6 !important;
    box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
}

.filter-label {
    font-weight: 500;
    margin-bottom: 5px;
    color: #ECEFF1;
    font-weight: 500;
}

.filter-item {
    flex: 1;
    min-width: 180px;
}

.card-title {
    font-size: 18px;
    color: #00BFA6;
    margin-bottom: 10px;
}
.small-btn {
    padding: 4px 12px;
    font-size: 12px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}

.small-btn:hover {
    background-color: #0056b3;
}

.status-text {
    font-size: 11px;
    color: #ccc;
    margin-top: 5px;
}

</style>

        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''

    dash_app.layout = serve_layout(colors, locations, dates, hours)

    register_callbacks(dash_app, colors)

    return dash_app