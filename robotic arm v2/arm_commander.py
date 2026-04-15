import requests
import time

ARM_URL = "http://192.168.4.1"  # your Pico W AP IP

def _get(path, timeout=10):
    try:
        requests.get(f"{ARM_URL}{path}", timeout=timeout)
    except Exception as e:
        print(f"  [ARM] Error on {path}: {e}")

def move_joint(num, angle, delay=1.0):
    """num: 1=base  2=shoulder  3=elbow"""
    angle = int(round(angle))
    print(f"  [ARM] Joint {num} → {angle}°")
    _get(f"/stepper?num={num}&angle={angle}")
    time.sleep(delay)

def move_all(base, shoulder, elbow, delay=1.5):
    move_joint(1, base,    delay=0.8)
    move_joint(2, shoulder,delay=0.8)
    move_joint(3, elbow,   delay=0.8)
    time.sleep(delay)

def gripper_open():
    print("  [ARM] Gripper OPEN")
    _get("/gripper?action=open")
    time.sleep(0.8)

def gripper_close():
    print("  [ARM] Gripper CLOSE")
    _get("/gripper?action=close")
    time.sleep(0.8)

def calibrate():
    print("  [ARM] Calibrating — do not touch arm!")
    _get("/calibrate", timeout=60)
    time.sleep(6)
    print("  [ARM] Calibration done")