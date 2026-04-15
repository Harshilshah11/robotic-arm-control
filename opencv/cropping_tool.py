import cv2
import numpy as np

img = cv2.imread("airplane.jpg")
temp = img.copy()

drawing = False
flag = False
ix = -1
iy = -1

def crop(event, x, y, flags, params):
    global flag, ix, iy, temp

    if event == 1:
        flag = True
        ix = x
        iy = y

    elif event == 0:
        if flag == True:
            temp = img.copy()
            cv2.rectangle(temp, (ix, iy), (x, y), (0, 0, 255), 1)

    elif event == 4:
        fx = x
        fy = y
        flag = False

        temp = img.copy()
        cv2.rectangle(temp, (ix, iy), (fx, fy), (0, 0, 255), 1)

        cropped = img[iy:fy, ix:fx]
        cv2.imshow("new_window", cropped)

cv2.namedWindow("window")
cv2.setMouseCallback("window", crop)

while True:
    cv2.imshow("window", temp)

    if cv2.waitKey(1) & 0xFF == ord('x'):
        break

cv2.destroyAllWindows()