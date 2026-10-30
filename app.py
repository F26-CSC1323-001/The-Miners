import requests
from flask import Flask, Response, jsonify, stream_with_context
from flask_cors import CORS
# This flask server should be ran in wsl terminal with first:
# activating the virtual environment running:
# source flask-env/bin/activate

app = Flask(__name__)
CORS(app)

CAMERA_IP = "http://192.168.1.175:8080"   # change to ip camera address

@app.route("/")
def home():
    return "<br><h1>Backend is running</h1>" # Show backend works

@app.route("/api/spots")
def get_spots():
    return jsonify({"spot1": "empty", "spot2": "occupied"}) # Example data returned from algorithm

@app.route("/api/frame")
# def htmlmessage():
#     return "<br><h1>Backend is running on /api/frame</h1>"
def frame():
    r = requests.get(f"{CAMERA_IP}/shot.jpg", timeout=5)
    return Response(r.content, mimetype="image/jpeg")

@app.route("/api/video")
#def htmlmessage1():
 #   return "<br><h1>Backend is running on /api/video</h1>"
def video():
    upstream = requests.get(f"{CAMERA_IP}/video", stream=True, timeout=10)
    return Response(
        stream_with_context(upstream.iter_content(chunk_size=4096)),
        content_type=upstream.headers.get("Content-Type", "multipart/x-mixed-replace"),
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) # run on port 5000
