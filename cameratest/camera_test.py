from ultralytics import YOLO
import cv2

# Load YOLO model (use 'yolov8n.pt' for better speed)
model = YOLO('yolov8n.pt')

# Open webcam (try 0 first, then 1 if needed)
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Error: Cannot open camera")
    exit()

# Set resolution (optional but helps performance)
cap.set(3, 640)  # width
cap.set(4, 480)  # height

while True:
    ret, frame = cap.read()

    if not ret or frame is None:
        print("Failed to grab frame")
        break

    # Run YOLO detection
    results = model(frame, stream=True)

    # Draw results
    for r in results:
        annotated_frame = r.plot()

    # Show output
    cv2.imshow("YOLOv8 Live Detection", annotated_frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()