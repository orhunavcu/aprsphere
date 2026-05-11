from flask import Flask, render_template, request, jsonify, send_from_directory
import subprocess
import json
import os

app = Flask(__name__, template_folder="templates", static_folder="templates/static")

CONFIG_FILE = "config.json"
process = None

DEFAULT_CONFIG = {
    "SERVER": "1",
    "CALLSIGN": "",
    "SSID": "10",
    "LAT": "",
    "LON": "",
    "SYMBOL_TABLE": "/",
    "SYMBOL": "-",
    "COMMENT": "",
    "INTERVAL": "900"
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

@app.route("/")
def index():
    return render_template("index.html", config=load_config())

@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(load_config())

@app.route("/api/config", methods=["POST"])
def set_config():
    save_config(request.json)
    return jsonify({"status": "ok"})

@app.route("/api/start", methods=["POST"])
def start():
    global process
    if process and process.poll() is None:
        return jsonify({"status": "already_running"})
    config = load_config()
    env = {**os.environ, **config}
    process = subprocess.Popen(["python", "main.py"], env=env)
    return jsonify({"status": "started", "pid": process.pid})

@app.route("/api/stop", methods=["POST"])
def stop():
    global process
    if process and process.poll() is None:
        process.terminate()
        process = None
        return jsonify({"status": "stopped"})
    return jsonify({"status": "not_running"})

@app.route("/api/status", methods=["GET"])
def status():
    global process
    running = process is not None and process.poll() is None
    return jsonify({"running": running, "pid": process.pid if running else None})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3169, debug=False)
