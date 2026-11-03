#____________________________________________________________#

# Algorithm for the Parking Spot Availibility Detection

#____________________________________________________________#

# Imports

import json
import os
import time
import cv2

#____________________________________________________________#

# Settings

CAMERA_URL = "rtsp:____" # 0 can be used for a webcam and a jpg can be used for a test photo

SPOTS_FILE = "spots.json"   # The spot boxes saved location
EDGE_THRESHOLD = 0.08       # The fraction needed for a spot to be considered "occupied"
CHECK_INTERVAL = 5          # The seconds between checks

GREEN = (0, 200, 0)         # OpenCV uses BGR for colors (not RGB)
RED = (0, 0, 255)

#____________________________________________________________#

# Grabs Frame

def grab_frame():
    cap = cv2.VideoCapture(CAMERA_URL)
    success, frame = cap.read()
    cap.release()
    if not success:
        return None
    return frame

#____________________________________________________________#

# Select The Parking Spots

def select_spots(frame):
    spots = []
    print("Draw a box around a spot, then press ENTER or SPACE.")
    print("When you've done every spot, press 'c' (or ESC) to finish.")

    while True:
        preview = frame.copy()
        for (x, y, w, h) in spots:
            cv2.rectangle(preview, (x, y), (x + w, y + h), GREEN, 2)

        x, y, w, h = cv2.selectROI("Select spots", preview, showCrosshair=False)
        if w == 0 or h == 0:
            break
        spots.append((int(x), int(y), int(w), int(h)))
    cv2.destroyWindow("Select spots")
    return spots

#____________________________________________________________#

# Creates / Loads Spots

def load_or_create_spots(frame, force_setup=False):
    if os.path.exists(SPOTS_FILE) and not force_setup:
        with open(SPOTS_FILE) as f:
            return json.load(f)

    spots = select_spots(frame)
    with open(SPOTS_FILE, "w") as f:
        json.dump(spots, f)
    return spots

#____________________________________________________________#

# Fraction of Pixels that are Edges

def edge_ratio(frame, spot):
    x, y, w, h = spot
    crop = frame[y:y + h, x:x + w]              # Crops the spot

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)   # Graycales the crop
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)     # Blurs the crop
    edges = cv2.Canny(blurred, 50, 150)             # The White pixels are edges

    return cv2.countNonZero(edges) / (w * h)

#____________________________________________________________#

# Parking Spot Checker

def check_spots(frame, spots):
    free_count = 0

    for i, spot in enumerate(spots):
        x, y, w, h = spot
        ratio = edge_ratio(frame, spot)
        occupied = ratio > EDGE_THRESHOLD

        if not occupied:
            free_count += 1

        color = RED if occupied else GREEN
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, f"{i + 1}: {ratio:.2f}", (x + 3, y + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    return free_count

#____________________________________________________________#

# The Main Function

def main():
    frame = grab_frame()
    while frame is None:
        print("Could not reach camera. Check CAMERA_URL. Retrying...")
        time.sleep(3)
        frame = grab_frame()

    spots = load_or_create_spots(frame)
    print(f"Monitoring {len(spots)} spots. Press 'q' to quit, 'r' to redo setup.")

    while True:
        frame = grab_frame()
        if frame is None:
            print("Lost camera connection, retrying...")
            time.sleep(3)
            continue

        free = check_spots(frame, spots)
        label = f"Free spots: {free}/{len(spots)}"
        cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 255, 255), 2)
        print(label)

        cv2.imshow("Parking Monitor", frame)
        key = cv2.waitKey(CHECK_INTERVAL * 1000) & 0xFF
        if key == ord("q"):
            break
        if key == ord("r"):
            spots = load_or_create_spots(frame, force_setup=True)

    cv2.destroyAllWindows()

#____________________________________________________________#

if __name__ == "__main__":
    main()

#____________________________________________________________#