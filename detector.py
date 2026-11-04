# detector.py
# Algorithm for the Parking Spot Availability Detection
#
# What this file does:
# Gets a picture from the camera
# Looks at each parking spot box that was drawn in setup_spots.py (saved in spots.json)
# Counts how many "edge" pixels are inside each box:
# Lots of edges = something is in the spot (a car)  -> "occupied"
# Few edges     = plain pavement                    -> "free"
# Saves the results so Flask (app.py) can send them to the website

import json        # reads the saved spot boxes from spots.json
import threading   # lets it run in the backgroun
import time        # used to pause between checks

import cv2         # OpenCV: image processing (edges, drawing boxes, ect)
import numpy       # needed to turn the downloaded picture into an image
import requests    # downloads the picture from the camera over HTTP

# These variables are prone to change
CAMERA_URL = "http://192.168.1.175:8080"   # IP Camera address
SPOTS_FILE = "spots.json"                  # created by setup_spots.py
EDGE_THRESHOLD = 0.05                      # fraction of edge pixels above which a spot is "occupied"
CHECK_INTERVAL = 3                         # seconds between checks

GREEN = (0, 200, 0)   # OpenCV uses BGR
RED = (0, 0, 255)

# Shared results. The detector thread writes them and Flask reads them,
# so they are only touched while holding the lock (see _loop and the get_ functions).
_lock = threading.Lock()
_status = {}            # results are dictionaries like {"spot1": "free", "spot2": "occupied"}
_annotated_jpg = None   # latest frame with boxes drawn on it


def grab_frame():
    # Download a picture from the camera, returns None if anything goes wrong
    try:
        r = requests.get(f"{CAMERA_URL}/shot.jpg", timeout=5)
        # turn the raw downloaded bytes into an OpenCV image
        arr = numpy.frombuffer(r.content, numpy.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)   # none if it isn't a valid image
    except requests.RequestException:
        # camera off, wrong address, or WiFi problem
        return None


def load_spots():
    # read the spot boxes from spots.json. Each spot is [x, y, width, height]
    try:
        with open(SPOTS_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        # setup_spots.py hasn't been run yet, so there are no spots to check
        return []


def edge_ratio(frame, spot):
    # return the fraction (0 to 1) of pixels in one spot that are edges
    x, y, w, h = spot
    crop = frame[y:y + h, x:x + w]               # cut out just this parking spot
    if crop.size == 0:
        return 0.0                               # box is outside the picture
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)     # edges don't need color
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)       # blur away small noise and texture
    edges = cv2.Canny(blurred, 50, 150)          # white pixels are edges
    # edge pixels divided by total pixels (edges.size also handles boxes cut off at the border)
    return cv2.countNonZero(edges) / edges.size


def check_spots(frame, spots):
    # check every spot. returns (results dictionary, picture with boxes drawn on it)
    result = {}
    annotated = frame.copy()     # draw on a copy so the original picture stays clean
    free = 0

    for i, (x, y, w, h) in enumerate(spots, start=1):    # numbering starts at 1
        ratio = edge_ratio(frame, (x, y, w, h))
        occupied = ratio > EDGE_THRESHOLD        # too many edges = a car is probably there
        if not occupied:
            free += 1
        result[f"spot{i}"] = "occupied" if occupied else "free"

        # draw the box and its score so you can tune EDGE_THRESHOLD by eye
        color = RED if occupied else GREEN
        cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
        cv2.putText(annotated, f"{i}: {ratio:.2f}", (x + 3, y + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # total free spots in the top-left corner of the picture
    cv2.putText(annotated, f"Free spots: {free}/{len(spots)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    return result, annotated


def _loop():
    # runs forever in the background: grab a picture, check the spots, save the results
    global _status, _annotated_jpg
    while True:
        try:
            spots = load_spots()        # reloaded every time, so new spots are picked up without a restart
            frame = grab_frame()
            if frame is not None and spots:
                result, annotated = check_spots(frame, spots)

                # shrink the picture before saving it so the website downloads less data
                h, w = annotated.shape[:2]
                if w > 640:
                    annotated = cv2.resize(annotated, (640, int(h * 640 / w)))
                # encode as a JPEG (quality 60 = smaller file)
                ok, jpg = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 60])

                # save the results where Flask can read them
                with _lock:
                    _status = result
                    if ok:
                        _annotated_jpg = jpg.tobytes()
            elif frame is None:
                print("Could not reach the camera. Check CAMERA_URL.")
        except Exception as e:
            # keep the loop alive even if one check fails
            print("Detector error:", e)
        time.sleep(CHECK_INTERVAL)      # wait before checking again


def start_detector():
    # called once by app.py to start the background checking
    # daemon=True means this thread stops automatically when the program exits
    threading.Thread(target=_loop, daemon=True).start()


def get_status():
    # latest results for Flask's /api/spots. returns a copy so it can't change mid-use
    with _lock:
        return dict(_status)


def get_annotated():
    # latest picture with boxes (JPEG bytes) for Flask's /api/annotated, or None if there isn't one yet
    with _lock:
        return _annotated_jpg