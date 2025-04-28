import json
from datetime import datetime
import speedtest
import time
import subprocess
import re
from threading import Event
from Database.database import get_db_connection
from modules.config import LOCATION_PIXEL_COORDS, PARAMETERS


stop_event = Event()

# Function to get WiFi RSSI on Windows using netsh
def get_rssi():
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True)
        match = re.search(r"Signal\s+:\s+(\d+)", result.stdout)
        return int(match.group(1)) if match else None
    except Exception as e:
        print(f"Error getting RSSI: {e}")
        return None

# Function to get packet loss, jitter, and latency using ping
def get_ping_stats():
    try:
        result = subprocess.run(['ping', '-n', '10', '8.8.8.8'], capture_output=True, text=True)
        output = result.stdout
        match_loss = re.search(r"(\d+)% packet loss", output)
        packet_loss = float(match_loss.group(1)) if match_loss else 0.0
        match_latency = re.search(r"Average = (\d+)ms", output)
        latency = float(match_latency.group(1)) if match_latency else 0.0
        jitter = 0.0  # Jitter estimation not available in ping
        return latency, jitter, packet_loss
    except Exception as e:
        print(f"Error getting ping stats: {e}")
        return None, None, None

# Function to get download and upload speeds using speedtest-cli
def get_speed():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1e6  # Mbps
        upload_speed = st.upload() / 1e6  # Mbps
        return download_speed, upload_speed
    except Exception as e:
        print(f"Error getting speed: {e}")
        return None, None

# Function to write data to a JSON file
def write_to_json_file(download_speed, upload_speed, latency_ms, jitter_ms, packet_loss, rssi,
                       location, position_x, position_y, run_no, filename=r"data/wifi_data.json"):
    try:
        try:
            with open(filename, 'r') as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = {}

        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "run_no": run_no,
            "location": {
                "position[x]": position_x,
                "position[y]": position_y,
                "position[name]": location
            },
            "download_speed": download_speed,
            "upload_speed": upload_speed,
            "latency_ms": latency_ms,
            "jitter_ms": jitter_ms,
            "packet_loss": packet_loss,
            "rssi": rssi
        }

        if location not in existing_data:
            existing_data[location] = []

        existing_data[location].append(entry)

        with open(filename, 'w') as f:
            json.dump(existing_data, f, indent=4)
    except Exception as e:
        print(f"Error writing to JSON file: {e}")


# Function to store data in MongoDB in nested format by location
def store_data_in_db(location_name, position_x, position_y, data):
    try:
        db = get_db_connection()
        wifi_data_col = db["wifi_data"]

        # Prepare new entry
        new_entry = {
            "timestamp": data['timestamp'],
            "run_no": data['run_no'],
            "location": {
                "position[x]": position_x,
                "position[y]": position_y,
                "position[name]": location_name
            },
            "download_speed": data['download_speed'],
            "upload_speed": data['upload_speed'],
            "latency_ms": data['latency_ms'],
            "jitter_ms": data['jitter_ms'],
            "packet_loss": data['packet_loss'],
            "rssi": data['rssi']
        }

        # Upsert by location_name: Push the new run data into the array
        wifi_data_col.update_one(
            {"_id": location_name},
            {"$push": {location_name: new_entry}},
            upsert=True
        )

        print(f"✅ Data stored under {location_name}")
    except Exception as e:
        print(f"❌ Error storing data in MongoDB: {e}")

# Main function to collect and store WiFi data
def collect_and_store_data(location_list, run_no):
    for location in location_list:
        if stop_event.is_set():
            print("Data collection interrupted.")
            break

        if len(location) != 3:
            print("Invalid location format. Skipping:", location)
            continue

        location_name, position_x, position_y = location

        print(f"[Run {run_no}] getting Data for {location_name}...")

        download_speed, upload_speed = get_speed()
        latency, jitter, packet_loss = get_ping_stats()
        rssi = get_rssi()

        if all(val is not None for val in [download_speed, upload_speed, latency]):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            write_to_json_file(
                download_speed, upload_speed, latency, jitter, packet_loss,
                rssi, location_name, position_x, position_y, run_no=run_no
            )

            data = {
                "timestamp": timestamp,
                "download_speed": download_speed,
                "upload_speed": upload_speed,
                "latency_ms": latency,
                "jitter_ms": jitter,
                "packet_loss": packet_loss,
                "rssi": rssi,
                "run_no": run_no
            }

            store_data_in_db(location_name, position_x, position_y, data)
            print(f"[Run {run_no}] Data saved at {timestamp} for {location_name}")
        else:
            print(f"[Run {run_no}] Data can't be saved at {timestamp} for {location_name}")
        time.sleep(5)
    print(f"[Run {run_no}] Data collection is Completed.")


def get_next_run_no():
    try:
        db = get_db_connection()
        wifi_data_col = db["wifi_data"]

        today = datetime.now().strftime("%Y-%m-%d")
        max_run = 0

        for doc in wifi_data_col.find():
            key = doc["_id"]
            if isinstance(doc.get(key), list):
                for entry in doc[key]:
                    if "run_no" in entry and "timestamp" in entry:
                        entry_date = entry["timestamp"].split(" ")[0]
                        if entry_date == today:
                            max_run = max(max_run, entry["run_no"])

        return max_run + 1
    except Exception as e:
        print(f"Error fetching run_no: {e}")
        return 1



def start_collection(location_list=None):
    if location_list is None:
        location_list = [(location, coords[0], coords[1]) for location, coords in LOCATION_PIXEL_COORDS.items()]
    run_no = get_next_run_no()
    print(f"Starting data collection for Run {run_no} across {len(location_list)} locations...")
    collect_and_store_data(location_list, run_no)
    return True
 

def stop_collection():
    stop_event.set()
    print("Data collection stopped.")
