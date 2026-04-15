import cv2
import numpy as np

FRAME_W, FRAME_H     = 800, 800
OBJECT_REAL_WIDTH_CM = 1.75    # measure your object
FOCAL_LENGTH_PX      = 600.0  # calibrate this!

TARGET_SHAPE = None  # set at runtime

def set_target(shape: str):
    global TARGET_SHAPE
    TARGET_SHAPE = shape.strip().capitalize()  # "Circle", "Square", "Rectangle"
    print(f"  [VISION] Target shape set to: {TARGET_SHAPE}")

def get_detection(frame):
    """
    Returns (cx, cy, depth_cm, shape, diameter_px) of best match or None
    Draws detections on frame in-place
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # White mask
    white_mask = cv2.inRange(hsv,
        np.array([0,   0,   180]),
        np.array([179, 50,  255]))

    # Black mask
    black_mask = cv2.inRange(hsv,
        np.array([0,   0,   0]),
        np.array([179, 255, 60]))

    combined = cv2.bitwise_or(white_mask, black_mask)

    # Morphology
    kernel  = np.ones((5,5), np.uint8)
    combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN,  kernel, iterations=2)
    combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best = None  # (area, cx, cy, depth, shape, diameter)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 1000 or area > 9000:
            continue

        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue

        epsilon = 0.02 * perimeter
        approx  = cv2.approxPolyDP(cnt, epsilon, True)

        rect = cv2.minAreaRect(cnt)
        (w, h) = rect[1]
        if w == 0 or h == 0:
            continue

        diameter     = max(w, h)
        aspect_ratio = max(w, h) / min(w, h)
        circularity  = (4 * np.pi * area) / (perimeter * perimeter)
        extent       = area / (w * h)

        # Shape classification (your exact logic)
        if circularity > 0.82 and len(approx) > 6:
            shape = "Circle"
        elif len(approx) == 4 and 0.85 <= aspect_ratio <= 1.15 and extent > 0.75:
            shape = "Square"
        elif len(approx) == 4:
            shape = "Rectangle"
        else:
            shape = "Unknown"

        # Filter by target
        if TARGET_SHAPE and shape != TARGET_SHAPE:
            # Still draw it but grey
            box = cv2.boxPoints(rect).astype(int)
            cv2.drawContours(frame, [box], 0, (100,100,100), 1)
            cv2.putText(frame, shape,
                       (int(rect[0][0])-40, int(rect[0][1])-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100,100,100), 1)
            continue

        # Depth estimate
        if diameter <= 0:
            continue
        depth = (OBJECT_REAL_WIDTH_CM * FOCAL_LENGTH_PX) / diameter

        cx = int(rect[0][0])
        cy = int(rect[0][1])

        # Draw target match — green
        box = cv2.boxPoints(rect).astype(int)
        cv2.drawContours(frame, [box], 0, (0,255,0), 2)
        cv2.circle(frame, (cx,cy), 6, (0,0,255), -1)
        cv2.putText(frame, f"{shape} {depth:.1f}cm",
                   (cx-50, cy-15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        cv2.putText(frame, f"D:{int(diameter)}px",
                   (cx-40, cy+20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,200,255), 1)

        # Keep largest matching contour
        if best is None or area > best[0]:
            best = (area, cx, cy, depth, shape, diameter)

    if best:
        _, cx, cy, depth, shape, diam = best
        return cx, cy, depth, shape, diam
    return None

def pixel_to_xyz(cx, cy, depth_cm):
    x = (cx - FRAME_W/2) * depth_cm / FOCAL_LENGTH_PX
    y = depth_cm
    z = -(cy - FRAME_H/2) * depth_cm / FOCAL_LENGTH_PX
    return x, y, z