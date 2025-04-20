import pandas as pd
import json
from datetime import datetime
from .utils import get_pixel_coords
import os
from Database.database import get_db_connection

def load_wifi_data():
    try:
        db = get_db_connection()
        collection = db["wifi_data"]
        records = []

        for doc in collection.find():
            location = doc["_id"]
            measurements = doc.get(location, [])
            for measurement in measurements:
                try:
                    timestamp = datetime.strptime(measurement['timestamp'], '%Y-%m-%d %H:%M:%S')
                    records.append({
                        'timestamp': timestamp,
                        'date': timestamp.strftime('%Y-%m-%d'),
                        'hour': timestamp.strftime('%H:00'),
                        'location': measurement['location']['position[name]'],
                        'download_speed': measurement['download_speed'],
                        'upload_speed': measurement['upload_speed'],
                        'latency_ms': measurement['latency_ms'],
                        'jitter_ms': measurement['jitter_ms'],
                        'packet_loss': measurement['packet_loss'],
                        'rssi': measurement['rssi'],
                        'run_no': measurement['run_no']
                    })
                except Exception as e:
                    print(f"⚠️ Skipping bad record: {e}")
                    continue

        return pd.DataFrame(records)
    except Exception as e:
        print(f"❌ Error fetching from DB: {e}")
        return pd.DataFrame()


def prepare_heatmap_data(df, selected_param):
    df = df.copy()
    df['x'], df['y'] = zip(*df['location'].map(get_pixel_coords))
    df = df.dropna(subset=[selected_param, 'x', 'y'])
    return df[['x', 'y', selected_param, 'location']]