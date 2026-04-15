import cv2
import numpy as np

fourcc = cv2.VideoWriter_fourcc(*'XVID')
cap = cv2.VideoCapture(0)
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

while True:
    ret, frame = cap.read()

    if ret:
            out.write(frame)  # Write the frame to the video file
            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    else:
            break

    # gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # cv2.imshow("window", gray_frame)

    if cv2.waitKey(1) & 0xFF == ord('x'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()