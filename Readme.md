# WiFi Performance Analysis

### Overview

This project is a **Dash-based web application** for monitoring and analyzing WiFi performance across different locations in a building. The app allows users to visualize key network performance metrics (such as download speed, upload speed, latency, jitter, and more) in real-time and make insightful data-driven decisions based on WiFi health. It uses **MongoDB** to store data and supports dynamic visualization through interactive charts, heatmaps, and trend analyses.

---

### **Features**

- **Real-time WiFi Data**: Monitor parameters like download/upload speed, latency, jitter, packet loss, and RSSI.
- **Location-based Analysis**: View performance metrics on a **per-location basis**.
- **Run Analysis**: Analyze data from specific runs for better insights.
- **Trend Analysis**: Visualize the trends over time for each parameter.
- **Heatmap View**: See WiFi performance on an interactive map.

---

### **Setup Instructions**

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-repository/wifi-dashboard.git
   cd wifi-dashboard
   ```

2. **Install Dependencies:**

   - Create a virtual environment (optional but recommended):
     ```bash
     python3 -m venv venv
     source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
     ```
   - Install required packages:
     ```bash
     pip install -r requirements.txt
     ```

3. **MongoDB Configuration:**

   - Set up **MongoDB** and ensure it’s running.
   - Update `modules/config.py` with the correct **MongoDB URI** and **collection** if needed:
     ```python
     DB_COLLECTIONS = {
         'wifi_data': 'wifi_data'  # Adjust this if your MongoDB collection name differs
     }
     ```

4. **Running the App:**

   - Start the Flask app (and Dash in parallel):
     ```bash
     python app.py
     ```

5. **Access the Dashboard**: Open a browser and go to:
   ```bash
   http://127.0.0.1:5000
   ```

---

### **How to Add or Remove Locations and Parameters**

To ensure flexibility and seamless management of locations and parameters, follow these guidelines:

#### **Adding/Removing Locations**

Locations are defined in the `modules/config.py` file under the `LOCATION_PIXEL_COORDS` dictionary. Each location has coordinates for positioning in heatmaps.

**To add a new location**:

1. Add the new location name and pixel coordinates to the `LOCATION_PIXEL_COORDS` dictionary:

   ```python
   LOCATION_PIXEL_COORDS = {
       "LOUNGE": (500, 200),
       "SDB": (100, 150),
       "GEC": (300, 120),
       "ECC": (220, 300),
       "FOODCOURT": (400, 250),
       "LIBRARY": (600, 180),  # ➕ New location
   }
   ```

2. Ensure that the new location is properly integrated into the **database schema** (MongoDB). The location should follow the format used in existing records:
   ```json
   "location": {
       "position[x]": 500,
       "position[y]": 200,
       "position[name]": "LIBRARY"
   }
   ```

**To remove a location**:

- Simply remove the corresponding entry from `LOCATION_PIXEL_COORDS`.

#### **Adding/Removing Parameters**

Parameters are managed in `modules/config.py` under the `PARAMETER_LABELS` dictionary. This dictionary holds both the parameter keys and their human-readable names for the UI.

**To add a new parameter**:

1. Add the parameter key and display name to `PARAMETER_LABELS`:
   ```python
   PARAMETER_LABELS = {
       'download_speed': 'Download Speed (Mbps)',
       'upload_speed': 'Upload Speed (Mbps)',
       'latency_ms': 'Latency (ms)',
       'jitter_ms': 'Jitter (ms)',
       'packet_loss': 'Packet Loss (%)',
       'rssi': 'RSSI (dBm)',
       'signal_quality': 'Signal Quality (%)',  # ➕ New parameter
   }
   ```
2. Add a corresponding color entry for this parameter in `COLORS` (to match the visual theme):

   ```python
   COLORS = {
       'download_speed': '#1f77b4',
       'upload_speed': '#ff7f0e',
       'latency_ms': '#2ca02c',
       'jitter_ms': '#d62728',
       'packet_loss': '#9467bd',
       'rssi': '#8c564b',
       'signal_quality': '#e377c2',  # ➕ New color
   }
   ```

3. Add logic for how this parameter should be displayed in the app. The `overview_callbacks.py` file already has a template for rendering cards; you might need to modify or extend the logic to account for the new parameter.

**To remove a parameter**:

- Remove the entry from both `PARAMETER_LABELS` and `COLORS` to prevent it from being displayed.

---

### **Managing Data Collection and Analysis**

- **Starting/Stopping Data Collection**:

  - The Flask app manages data collection via the `/collection` route. Use the interface to **start** or **stop** the collection thread.
  - This allows you to capture data dynamically while the app is running.

- **Accessing WiFi Data**:
  - The app fetches WiFi data from MongoDB and dynamically loads it for analysis using various Dash components.
  - Data for each run, location, and parameter is collected and displayed in **real-time**.

---
