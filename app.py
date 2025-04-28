from flask import Flask, redirect, jsonify, request, render_template
from threading import Thread
from src.main import start_collection, stop_collection, stop_event
from dash_app import create_dash_app
from Database.database import get_db_connection

proj = Flask(__name__)
dash_app = create_dash_app(proj)

collection_thread = None  # Global thread reference

@proj.route('/')
def dashboard():
    return redirect('/dashboard/')

@proj.route('/showdata')
def showdata():
    try:
        db = get_db_connection()
        wifi_data_col = db["wifi_data"]
        data = list(wifi_data_col.find({}, {"_id": 0}).sort("timestamp", -1).limit(100))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

@proj.route('/collection/status')
def collection_status():
    is_running = collection_thread and collection_thread.is_alive()
    return {'status': is_running}


#Combined Start/Stop UI + Logic Route
@proj.route('/collection', methods=['GET', 'POST'])
def collection():
    global collection_thread
    message = ""
    status = False

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'start':
            if collection_thread and collection_thread.is_alive():
                status = True
                message = "⚠️ Data collection is already running!"
            else:
                stop_event.clear()
                # loc = [['ECC', 67.12, -43.45], ['GEC', 70.21, -40.31], ['SDB', 65.78, -42.5],
                #        ['FOODCOURT', 68.33, -41.25], ['LOUNGE', 69.0, -39.9]]
                collection_thread = Thread(target=start_collection)
                collection_thread.start()
                status = True
                message = "🚀 Data Collection Started"
        elif action == 'stop':
            stop_collection()
            if collection_thread and collection_thread.is_alive():
                collection_thread.join(timeout=5)
                message = "🛑 Data Collection Stopped"
            else:
                message = "⚠️ No active data collection to stop"

    # ✅ Check if thread is still alive after the POST request logic
    if collection_thread and collection_thread.is_alive():
        status = True
    else:
        status = False

    return render_template("collection.html", message=message, status=status)


# Run app
if __name__ == "__main__":
    proj.run(debug=True)
