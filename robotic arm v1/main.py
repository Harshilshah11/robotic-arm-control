import requests
import time
import math

BASE = "http://192.168.4.1"

# Link lengths in CM — from your Pico code
L1 = 18   # upper arm
L2 = 21   # forearm

# Joint limits — from your Joint() constructors in Pico
J1_MIN, J1_MAX = -175,  175
J2_MIN, J2_MAX =  -20,   70
J3_MIN, J3_MAX =  -90,   80

# ── IK: proper geometric cosine-rule (zero error) ─────────────────────────────
# FK model (matches Pico):
#   r = L1*cos(j2) + L2*cos(j2+j3)   <- horizontal reach
#   z = L1*sin(j2) + L2*sin(j2+j3)   <- height
#
# Cosine rule gives exact solution, no brute force needed.

def solve_ik(x, y, z):
    """
    x, y = horizontal position (cm)
    z    = height (cm)
    Returns (j1, j2, j3) as integers, or None if unreachable.
    Picks the elbow-down solution (j3 negative) which stays in J3 range.
    """
    # J1: base yaw from X, Y
    j1 = math.degrees(math.atan2(y, x))
    if not (J1_MIN <= j1 <= J1_MAX):
        return None, f"J1={j1:.1f} out of range"

    # Reach in the arm's vertical plane
    r = math.sqrt(x**2 + y**2)
    D = math.sqrt(r**2 + z**2)

    if D > L1 + L2:
        return None, f"too far: D={D:.2f}cm, max={L1+L2}cm"
    if D < abs(L1 - L2):
        return None, f"too close: D={D:.2f}cm, min={abs(L1-L2)}cm"

    # J3 via cosine rule  (two solutions: elbow-up +, elbow-down -)
    cos_j3 = (D**2 - L1**2 - L2**2) / (2.0 * L1 * L2)
    cos_j3 = max(-1.0, min(1.0, cos_j3))

    best = None
    best_err = float('inf')

    for j3d in (math.degrees(math.acos(cos_j3)), -math.degrees(math.acos(cos_j3))):
        if not (J3_MIN <= j3d <= J3_MAX):
            continue
        j3r = math.radians(j3d)
        k1  = L1 + L2 * math.cos(j3r)
        k2  = L2 * math.sin(j3r)
        j2d = math.degrees(math.atan2(z, r) - math.atan2(k2, k1))
        if not (J2_MIN <= j2d <= J2_MAX):
            continue
        # Verify with FK
        t2, t3 = math.radians(j2d), j3r
        r_fk = L1*math.cos(t2) + L2*math.cos(t2+t3)
        z_fk = L1*math.sin(t2) + L2*math.sin(t2+t3)
        err = math.sqrt((r_fk - r)**2 + (z_fk - z)**2)
        if err < best_err:
            best_err = err
            best = (j1, j2d, j3d)

    if best is None:
        return None, "reachable but no solution within joint limits"

    j1, j2, j3 = best
    return (int(j1), int(j2), int(j3)), f"error={best_err:.4f}cm"


# ── Send with retry (Pico sends response AFTER motor finishes) ─────────────────
# CRITICAL: always send angles as integers — Pico does int(angle_str)
#           and crashes on "0.0", "45.0" etc.

def send(url, retries=3, timeout=30):
    for i in range(retries):
        try:
            res = requests.get(url, timeout=timeout)
            return res.status_code
        except requests.exceptions.ConnectionError:
            print(f"  retry {i+1}/{retries}...")
            time.sleep(1.5)
        except requests.exceptions.ConnectTimeout:
            print("  ERROR: timeout — connected to RoboticArm_AP?")
            return None
        except Exception as e:
            print(f"  ERROR: {e}")
            return None
    print("  ERROR: failed after retries")
    return None


# ── FK display helper ──────────────────────────────────────────────────────────

def show_fk(j2, j3):
    t2, t3 = math.radians(j2), math.radians(j3)
    r = L1*math.cos(t2) + L2*math.cos(t2+t3)
    z = L1*math.sin(t2) + L2*math.sin(t2+t3)
    return r, z


# ── Main loop ──────────────────────────────────────────────────────────────────

print("Robotic Arm Controller  |  WiFi: RoboticArm_AP / 12345678")
print(f"L1={L1}cm  L2={L2}cm  |  Workspace: reach 0-{L1+L2}cm, height ~-10 to 35cm")
print()
print("Commands:")
print("  move X Y Z        — move to position in cm  (e.g. move 30 0 10)")
print("  joint N ANGLE     — move one joint directly  (e.g. joint 2 45)")
print("  fk J2 J3          — show forward kinematics  (e.g. fk 30 -20)")
print("  open / close      — gripper")
print("  calibrate         — home all joints")
print("  quit")
print("-" * 55)

while True:
    try:
        raw = input("arm> ").strip().split()
    except (KeyboardInterrupt, EOFError):
        print("\nBye!")
        break

    if not raw:
        continue

    cmd = raw[0].lower()

    # ── quit ──────────────────────────────────────────────────────────────────
    if cmd == "quit":
        break

    # ── gripper ───────────────────────────────────────────────────────────────
    elif cmd == "open":
        code = send(f"{BASE}/gripper?action=open")
        if code: print(f"  gripper open [{code}]")

    elif cmd == "close":
        code = send(f"{BASE}/gripper?action=close")
        if code: print(f"  gripper close [{code}]")

    # ── calibrate ─────────────────────────────────────────────────────────────
    elif cmd == "calibrate":
        print("  Calibrating... (~10s)")
        code = send(f"{BASE}/calibrate", timeout=60)
        if code: print(f"  done [{code}]")

    # ── fk J2 J3 ──────────────────────────────────────────────────────────────
    elif cmd == "fk" and len(raw) == 3:
        try:
            j2, j3 = float(raw[1]), float(raw[2])
            r, z = show_fk(j2, j3)
            print(f"  FK: J2={j2}° J3={j3}° -> reach={r:.2f}cm  height={z:.2f}cm")
        except ValueError:
            print("  Usage: fk J2 J3")

    # ── joint N ANGLE ─────────────────────────────────────────────────────────
    elif cmd == "joint" and len(raw) == 3:
        try:
            n     = int(raw[1])
            angle = int(float(raw[2]))   # int() — Pico crashes on "45.0"
            if n not in (1, 2, 3):
                print("  Joint must be 1, 2 or 3")
            else:
                code = send(f"{BASE}/stepper?num={n}&angle={angle}")
                if code: print(f"  joint {n} -> {angle}° [{code}]")
        except ValueError:
            print("  Usage: joint N ANGLE  (e.g. joint 2 45)")

    # ── move X Y Z ────────────────────────────────────────────────────────────
    elif cmd == "move" and len(raw) == 4:
        try:
            x, y, z = float(raw[1]), float(raw[2]), float(raw[3])

            angles, info = solve_ik(x, y, z)

            if angles is None:
                print(f"  UNREACHABLE: {info}")
                continue

            j1, j2, j3 = angles
            r_fk, z_fk = show_fk(j2, j3)

            print(f"  IK   J1={j1}°  J2={j2}°  J3={j3}°  ({info})")
            print(f"  FK   reach={r_fk:.2f}cm  height={z_fk:.2f}cm  (target r={math.sqrt(x**2+y**2):.2f} z={z:.2f})")

            # Send as integers — Pico does int(angle_str), floats crash it
            code = send(f"{BASE}/stepper?num=1&angle={j1}")
            if code: print(f"  joint 1 -> {j1}° [{code}]")
            time.sleep(0.5)

            code = send(f"{BASE}/stepper?num=2&angle={j2}")
            if code: print(f"  joint 2 -> {j2}° [{code}]")
            time.sleep(0.5)

            code = send(f"{BASE}/stepper?num=3&angle={j3}")
            if code: print(f"  joint 3 -> {j3}° [{code}]")

        except ValueError:
            print("  Usage: move X Y Z  (e.g. move 30 0 10)")

    else:
        print("  Unknown: move X Y Z | joint N ANGLE | fk J2 J3 | open | close | calibrate | quit")
