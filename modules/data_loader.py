# modules/data_loader.py
import pandas as pd
from datetime import datetime
from modules.utils import get_pixel_coords
from modules.config import PARAMETERS, DB_COLLECTIONS
from Database.database import get_db_connection

def load_wifi_data():
    try:
        # Establish a connection to the MongoDB database
        db = get_db_connection()
        # Fetch the collection name dynamically from the config
        collection = db[DB_COLLECTIONS['wifi_data']]
        
        records = []

        # Iterate through all the documents in the collection
        for doc in collection.find():
            location = doc["_id"]
            measurements = doc.get(location, [])
            
            for measurement in measurements:
                try:
                    # Parse the timestamp from the measurement data
                    timestamp = datetime.strptime(measurement['timestamp'], '%Y-%m-%d %H:%M:%S')
                    record = {
                        'timestamp': timestamp,
                        'date': timestamp.strftime('%Y-%m-%d'),
                        'hour': timestamp.strftime('%H:00'),
                        'location': measurement['location']['position[name]'],
                        'run_no': measurement['run_no']
                    }

                    # Dynamically fetch all parameters from config
                    for param in PARAMETERS:
                        record[param] = measurement.get(param, None)

                    # Add the record to the list of records
                    records.append(record)
                except Exception as e:
                    print(f"⚠️ Skipping bad record: {e}")
                    continue

        # Return the data as a pandas DataFrame
        return pd.DataFrame(records)
    except Exception as e:
        print(f"❌ Error fetching from DB: {e}")
        return pd.DataFrame()

def prepare_heatmap_data(df, selected_param):
    from modules.config import PARAMETERS

    # Validate if the selected parameter exists in the config
    if selected_param not in PARAMETERS:
        raise ValueError(f"Invalid parameter: {selected_param}")

    df = df.copy()
    
    # Apply the get_pixel_coords function to map the location names to their pixel coordinates
    df['x'], df['y'] = zip(*df['location'].map(get_pixel_coords))
    
    # Drop any rows with missing values for the selected parameter or pixel coordinates
    df = df.dropna(subset=[selected_param, 'x', 'y'])
    
    # Return the dataframe with x, y, selected parameter, and location
    return df[['x', 'y', selected_param, 'location']]
