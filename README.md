# Robotic Arm

ESP32-based robotic arm with vision-guided pick & place.

## Structure

| Folder | Description |
|--------|-------------|
| `robotic arm v1/` | ESP32 (MicroPython) arm controller + web UI |
| `cameratest/` | PC-side YOLOv8 object detection |
| `opencv/` | OpenCV utilities and experiments |
| `references/` | Niryo One 3D models and docs |

## Stack

- ESP32 running MicroPython (arm controller)
- Python + OpenCV + YOLOv8 (PC-side vision)

---

## Setup

### 1. Install PC dependencies

```bash
pip install opencv-python ultralytics
```

### 2. Flash ESP32

Upload `robotic arm v1/vision_auto_pick.py` (and `arnobot.jpeg`) to the ESP32 using Thonny or mpremote.

---

## Running

### Arm Controller (ESP32)

Run `vision_auto_pick.py` on the ESP32. It starts a WiFi access point:

```
SSID:     RoboticArm_AP
Password: 12345678
```

Open a browser and go to `http://192.168.4.1` to access the control UI.

**UI features:**
- Axis 1/2/3 sliders and angle input
- Gripper open/close
- Calibration
- Save/run Position 1 & 2
- Pick & Place automation

### YOLOv8 Camera Detection (PC)

```bash
cd cameratest
python camera_test.py
```

Opens webcam feed with live YOLOv8 object detection. Press `q` to quit.

> If camera doesn't open, change `cv2.VideoCapture(1, ...)` to `cv2.VideoCapture(0, ...)` in `camera_test.py`.

---

## Hardware

- **Controller**: ESP32
- **Joints**: 3 stepper motors (base, shoulder, elbow) + 1 servo (gripper)
- **Limit switches**: Pins 2, 3, 4 (used during calibration)
- **Camera**: USB webcam (PC-side)
