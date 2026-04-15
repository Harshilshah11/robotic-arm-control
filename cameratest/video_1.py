import cv2 

cam=cv2.VideoCapture(1)

frame_width=int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height=int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

while True:
    ret, frame = cam.read()

    # Display the captured frame
    cv2.imshow('Camera', frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()    