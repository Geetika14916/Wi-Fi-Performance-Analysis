# modules/safe_data_loader.py
import pandas as pd
from modules.data_loader import load_wifi_data

def load_and_prepare_wifi_data():
    df = load_wifi_data()
    if df.empty:
        return pd.DataFrame()
    
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    return df

def get_available_dates(df):
    return sorted(df['date'].unique())

def get_available_runs(df, selected_date):
    if df.empty:
        return []
    return sorted(df[df['date'] == selected_date]['run_no'].unique().tolist())

def get_aggregated_data(df, selected_date, selected_run):
    filtered = df[(df['date'] == selected_date) & (df['run_no'] == selected_run)]
    if filtered.empty:
        return pd.DataFrame()

    agg = filtered.groupby('location').agg({
        'download_speed': 'mean',
        'upload_speed': 'mean',
        'latency_ms': 'mean',
        'jitter_ms': 'mean',
        'packet_loss': 'mean',
        'rssi': 'mean',
        'timestamp': 'count'
    }).reset_index().rename(columns={'timestamp': 'count'})
    return agg
