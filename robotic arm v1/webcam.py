import cv2

# Open the default camera (0 = primary webcam)
cap = cv2.VideoCapture(1)

# Check if camera opened successfully
if not cap.isOpened():
    print("Error: Cannot open camera")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # If frame not read properly
    if not ret:
        print("Error: Can't receive frame")
        break

    # Display the resulting frame
    cv2.imshow('Video Capture', frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()