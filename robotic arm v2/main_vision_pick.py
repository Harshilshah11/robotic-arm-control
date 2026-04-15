import cv2
import time
from enum import Enum
from vision import get_detection, pixel_to_xyz, set_target, FRAME_W, FRAME_H
from arm_commander import move_all, move_joint, gripper_open, gripper_close, calibrate
from ik_mirror import solve_ik

# ── Tune these ────────────────────────────────────────
ALIGN_TOL  = 25      # px — acceptable centering error
PICK_Z_CM  = 4.0     # grip height above table (cm)
SAFE_Z_CM  = 18.0    # lift height (cm)
PLACE      = (45, 50, -20)   # (base°, shoulder°, elbow°) — tune via web UI!
# ─────────────────────────────────────────────────────

class S(Enum):
    IDLE      = 0
    CALIBRATE = 1
    SEARCH    = 2
    CENTER    = 3
    DESCEND   = 4
    GRIP      = 5
    LIFT      = 6
    PLACE     = 7
    RELEASE   = 8
    HOME      = 9
    DONE      = 10

COLORS = {
    S.IDLE:(180,180,180),    S.CALIBRATE:(255,165,0),
    S.SEARCH:(0,255,255),    S.CENTER:(255,165,0),
    S.DESCEND:(50,50,255),   S.GRIP:(0,0,255),
    S.LIFT:(0,255,0),        S.PLACE:(255,0,255),
    S.RELEASE:(0,255,255),   S.HOME:(200,200,200),
    S.DONE:(0,200,0)
}

def ask_target():
    shape = input("\nEnter shape to pick (Circle / Square / Rectangle): ").strip()
    while shape.capitalize() not in ["Circle", "Square", "Rectangle"]:
        shape = input("  Invalid. Enter Circle, Square or Rectangle: ").strip()
    set_target(shape)
    return shape.capitalize()

# ── Init ──────────────────────────────────────────────
print("=" * 45)
print("  VISION PICK & PLACE — Shape Detection")
print("=" * 45)
input("1. Connect laptop to 'RoboticArm_AP' WiFi\n2. Press Enter to continue...")

target = ask_target()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)

state       = S.CALIBRATE
pick_angles = None
scan_dir    = 1
scan_base   = 0

print("\nStarting... press 'q' to quit, 'r' to reset, 'n' for new shape\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Your exact preprocessing
    frame = cv2.flip(frame, 1)
    frame = frame[0:800, 0:800]

    det = get_detection(frame)

    # ── CALIBRATE ────────────────────────────────────
    if state == S.CALIBRATE:
        calibrate()
        gripper_close()
        state = S.SEARCH

    # ── SEARCH ───────────────────────────────────────
    elif state == S.SEARCH:
        if det:
            state = S.CENTER
        else:
            # Sweep base left/right to scan workspace
            scan_base += 8 * scan_dir
            if abs(scan_base) > 70:
                scan_dir *= -1
            move_joint(1, scan_base, delay=0.2)

    # ── CENTER ───────────────────────────────────────
    elif state == S.CENTER:
        if not det:
            state = S.SEARCH
        else:
            cx, cy, depth, shape, diam = det
            ex = cx - FRAME_W // 2
            ey = cy - FRAME_H // 2

            # Error crosshair
            cv2.line(frame,(FRAME_W//2,0),(FRAME_W//2,FRAME_H),(255,255,0),1)
            cv2.line(frame,(0,FRAME_H//2),(FRAME_W,FRAME_H//2),(255,255,0),1)
            cv2.putText(frame, f"err x={ex} y={ey}",
                       (10,70), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,255,0),2)

            if abs(ex) < ALIGN_TOL and abs(ey) < ALIGN_TOL:
                x, y, z  = pixel_to_xyz(cx, cy, depth)
                angles   = solve_ik(x, y, PICK_Z_CM)
                if angles:
                    pick_angles = angles
                    state = S.DESCEND
                else:
                    print("  IK failed — object out of reach")
                    state = S.SEARCH
            else:
                # Nudge base to reduce X error
                nudge = scan_base - ex * 0.04
                move_joint(1, nudge, delay=0.1)

    # ── DESCEND ──────────────────────────────────────
    elif state == S.DESCEND:
        gripper_open()
        move_all(*pick_angles)
        state = S.GRIP

    # ── GRIP ─────────────────────────────────────────
    elif state == S.GRIP:
        gripper_close()
        time.sleep(0.5)
        state = S.LIFT

    # ── LIFT ─────────────────────────────────────────
    elif state == S.LIFT:
        b, _, _ = pick_angles
        lift = solve_ik(0, 15, SAFE_Z_CM)
        if lift:
            move_all(b, lift[1], lift[2])
        state = S.PLACE

    # ── PLACE ────────────────────────────────────────
    elif state == S.PLACE:
        move_all(*PLACE)
        time.sleep(1)
        state = S.RELEASE

    # ── RELEASE ──────────────────────────────────────
    elif state == S.RELEASE:
        gripper_open()
        time.sleep(0.5)
        gripper_close()
        state = S.HOME

    # ── HOME ─────────────────────────────────────────
    elif state == S.HOME:
        move_all(0, 0, 0)
        time.sleep(1)
        state = S.DONE

    # ── DONE ─────────────────────────────────────────
    elif state == S.DONE:
        cv2.putText(frame, "DONE! Press 'n' for new shape or 'q' to quit",
                   (10, FRAME_H//2), cv2.FONT_HERSHEY_SIMPLEX,
                   0.6, (0,255,0), 2)

    # ── HUD ──────────────────────────────────────────
    col = COLORS.get(state, (255,255,255))
    cv2.rectangle(frame, (0,0),(FRAME_W,40), col, -1)
    cv2.putText(frame, f"STATE: {state.name}  |  TARGET: {target}",
               (10,28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)

    cv2.imshow("Vision Pick & Place", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    elif key == ord('r'):
        print("  Manual reset to SEARCH")
        scan_base = 0
        state = S.SEARCH
    elif key == ord('n'):
        # Pick a new shape without restarting
        target = ask_target()
        scan_base = 0
        state = S.SEARCH
        print(f"  New target: {target} — searching...")

cap.release()
cv2.destroyAllWindows()