# setup_spots.py
# run this whenever the IP camera moves to mark where each parking spot is.
# It takes a picture from the camera, lets you draw a box around every spot,
# and saves the boxes to spots.json for detector.py to use.

import json   # saves the boxes to a file
import cv2    # OpenCV: shows the picture and lets you draw boxes

# grab_frame, SPOTS_FILE and GREEN come from detector.py so the settings live in one place
from detector import grab_frame, SPOTS_FILE, GREEN

frame = grab_frame()    # one picture from the camera
if frame is None:
    # stop with a clear message if the camera can't be reached
    raise SystemExit("Could not reach the camera. Check CAMERA_URL in detector.py.")

spots = []   # each spot will be [x, y, width, height]
print("Draw a box around a spot, then press ENTER or SPACE.")
print("When you've done every spot, press 'c' (or ESC) to finish.")

while True:
    # redraw the boxes you've already made so you can see what's done
    preview = frame.copy()
    for (x, y, w, h) in spots:
        cv2.rectangle(preview, (x, y), (x + w, y + h), GREEN, 2)

    # opens a window where you drag a box. Returns (x, y, width, height).
    x, y, w, h = cv2.selectROI("Select spots", preview, showCrosshair=False)
    if w == 0 or h == 0:
        break    # pressing 'c' or ESC returns an empty box, which means "I'm finished"
    spots.append([int(x), int(y), int(w), int(h)])

cv2.destroyAllWindows()

# save all boxes so detector.py can load them
with open(SPOTS_FILE, "w") as f:
    json.dump(spots, f)
print(f"Saved {len(spots)} spots to {SPOTS_FILE}")