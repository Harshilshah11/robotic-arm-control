import cv2
import numpy as np
import requests
import time

PICO_IP = "192.168.4.1"

cap = cv2.VideoCapture(1)

CENTER_TOLERANCE = 40   # pixels
last_pick_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    center_x = w // 2
    center_y = h // 2

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Detect BLUE (change if needed)
    lower = np.array([100,150,50])
    upper = np.array([140,255,255])

    mask = cv2.inRange(hsv, lower, upper)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        cnt = max(contours, key=cv2.contourArea)

        if cv2.contourArea(cnt) > 1000:
            x,y,wc,hc = cv2.boundingRect(cnt)
            cx = x + wc//2
            cy = y + hc//2

            # Draw
            cv2.circle(frame, (cx, cy), 5, (0,0,255), -1)
            cv2.line(frame, (center_x,0), (center_x,480), (255,0,0), 2)

            # 🔁 ALIGNMENT LOGIC
            if cx < center_x - CENTER_TOLERANCE:
                print("Move LEFT")
                requests.get(f"http://{PICO_IP}/stepper?num=1&angle=-5")

            elif cx > center_x + CENTER_TOLERANCE:
                print("Move RIGHT")
                requests.get(f"http://{PICO_IP}/stepper?num=1&angle=5")

            else:
                print("CENTERED 🎯")

                # ⏱ Prevent repeated picking
                if time.time() - last_pick_time > 3:
                    print("PICK OBJECT")
                    requests.get(f"http://{PICO_IP}/auto")
                    last_pick_time = time.time()

    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()