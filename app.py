# Flask server that returns routes that can be accessed with JS

import requests
from flask import Flask, Response, jsonify, stream_with_context
from flask_cors import CORS
from detector import CAMERA_URL as CAMERA_IP, start_detector, get_status, get_annotated

# This flask server should be ran in wsl terminal with first:
# activating the virtual environment running:
# source flask-env/bin/activate

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "<br><h1>Backend is running</h1>"

@app.route("/123")
def tmp():
    return "<br><h1>you found me!</h1>"
    
@app.route("/api/spots")
def get_spots():
    return jsonify(get_status()) # real results from the algorithm

@app.route("/api/annotated")
def annotated():
    jpg = get_annotated()
    if jpg is None:
        return "No frame processed yet", 503
    return Response(jpg, mimetype="image/jpeg")

@app.route("/api/frame")
def frame():
    r = requests.get(f"{CAMERA_IP}/shot.jpg", timeout=5)
    return Response(r.content, mimetype="image/jpeg")

@app.route("/api/video")
def video():
    upstream = requests.get(f"{CAMERA_IP}/video", stream=True, timeout=10)
    return Response(
        stream_with_context(upstream.iter_content(chunk_size=4096)),
        content_type=upstream.headers.get("Content-Type", "multipart/x-mixed-replace"),
    )

if __name__ == "__main__":
    start_detector()  # begins checking the camera in the background
    app.run(host="0.0.0.0", port=5000)