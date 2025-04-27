# modules/config.py

# 📊 Parameters and their display names
PARAMETER_LABELS = {
    'download_speed': 'Download Speed (Mbps)',
    'upload_speed': 'Upload Speed (Mbps)',
    'latency_ms': 'Latency (ms)',
    'jitter_ms': 'Jitter (ms)',
    'packet_loss': 'Packet Loss (%)',
    'rssi': 'RSSI (dBm)'
}

# List of parameters
PARAMETERS = list(PARAMETER_LABELS.keys())

# 📍 Location pixel coordinates (for heatmap positioning)
LOCATION_PIXEL_COORDS = {
    "SDB": (100, 150),
    "GEC": (300, 120),
    "ECC": (220, 300),
    "FOODCOURT": (400, 250),
    "LOUNGE": (500, 200)
}

# 🎨 Color theme
COLORS = {
    'background': '#15202b',
    'text': 'white',
    'download_speed': '#1f77b4',
    'upload_speed': '#ff7f0e',
    'latency_ms': '#2ca02c',
    'jitter_ms': '#d62728',
    'packet_loss': '#9467bd',
    'rssi': '#8c564b'
}
