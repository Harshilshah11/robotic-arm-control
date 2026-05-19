import pybullet as p
import pybullet_data
import time
import math

# ── Setup ─────────────────────────────────────────
p.connect(p.GUI)
p.setGravity(0, 0, -9.81)
p.setAdditionalSearchPath(pybullet_data.getDataPath())

robot = p.loadURDF("C:/Users/Harshil/Desktop/Robotic arm/simulation/niryoone/niryoone.urdf", useFixedBase=True)

# change these indices based on your robot
JOINTS = [0, 1, 2]  
END_EFFECTOR = 2

# ── Arm parameters (same as your real robot) ─────
L1 = 18
L2 = 21

J1_MIN, J1_MAX = -175, 175
J2_MIN, J2_MAX = -20, 70
J3_MIN, J3_MAX = -90, 90


# ── IK (same logic) ──────────────────────────────
def solve_ik(x, y, z):
    j1 = math.degrees(math.atan2(y, x))
    if not (J1_MIN <= j1 <= J1_MAX):
        return None, "J1 out"

    r = math.sqrt(x**2 + y**2)
    D = math.sqrt(r**2 + z**2)

    if D > L1 + L2:
        return None, "too far"
    if D < abs(L1 - L2):
        return None, "too close"

    cos_j3 = (D**2 - L1**2 - L2**2) / (2 * L1 * L2)
    cos_j3 = max(-1, min(1, cos_j3))

    best = None

    for j3d in (math.degrees(math.acos(cos_j3)), -math.degrees(math.acos(cos_j3))):
        if not (J3_MIN <= j3d <= J3_MAX):
            continue

        j3r = math.radians(j3d)
        k1 = L1 + L2 * math.cos(j3r)
        k2 = L2 * math.sin(j3r)

        j2d = math.degrees(math.atan2(z, r) - math.atan2(k2, k1))

        if not (J2_MIN <= j2d <= J2_MAX):
            continue

        best = (j1, j2d, j3d)

    if best is None:
        return None, "no solution"

    return tuple(map(int, best)), "ok"


# ── Move joints ──────────────────────────────────
def move_joints(j1, j2, j3):
    targets = [j1, j2, j3]

    for i, j in enumerate(JOINTS):
        p.setJointMotorControl2(
            robot,
            j,
            p.POSITION_CONTROL,
            targetPosition=math.radians(targets[i]),
            force=50
        )


# ── Get end position ─────────────────────────────
def get_pose():
    state = p.getLinkState(robot, END_EFFECTOR)
    return state[0]

l1 = 18
l2 = 21
l3 = 35

def inverse_kinematics(x, y, z):
    # Base rotation
    theta1 = math.atan2(y, x)

    # Planar distance
    r = math.sqrt(x**2 + y**2)
    z_eff = z - l1   # adjust for base height

    # Cosine law
    D = (r**2 + z_eff**2 - l2**2 - l3**2) / (2 * l2 * l3)

    # Check reachability
    if D > 1 or D < -1:
        return None  # unreachable

    # Elbow angle
    theta3 = math.acos(D)

    # Shoulder angle
    theta2 = math.atan2(z_eff, r) - math.atan2(
        l3 * math.sin(theta3),
        l2 + l3 * math.cos(theta3)
    )

    # Convert to degrees
    theta1 = math.degrees(theta1)
    theta2 = math.degrees(theta2)
    theta3 = math.degrees(theta3)

    return theta1, theta2, theta3

# ── CLI loop ─────────────────────────────────────
print("Commands: move x y z | joint n angle | fk | quit")

while True:
    p.stepSimulation()
    time.sleep(1 / 240)

    try:
        cmd = input("arm> ").split()
    except:
        break

    if not cmd:
        continue

    if cmd[0] == "quit":
        break

    elif cmd[0] == "move" and len(cmd) == 4:
        x, y, z = map(float, cmd[1:])

        angles = inverse_kinematics(x, y, z)

        if angles is None:
            print("Error: unreachable")
            continue

        j1, j2, j3 = angles
        print("IK:", (round(j1,1), round(j2,1), round(j3,1)))

        move_joints(j1, j2, j3)
        time.sleep(1)

        px, py, pz = get_pose()

        print("Target :", x, y, z)
        print("Actual :", round(px,2), round(py,2), round(pz,2))

        error = math.sqrt((px-x)**2 + (py-y)**2 + (pz-z)**2)

    elif cmd[0] == "joint" and len(cmd) == 3:
        j = int(cmd[1])
        angle = float(cmd[2])

        p.setJointMotorControl2(
            robot,
            JOINTS[j-1],
            p.POSITION_CONTROL,
            targetPosition=math.radians(angle),
            force=50
        )
    elif cmd[0] == "move" and len(cmd) == 4:
        x, y, z = map(float, cmd[1:])

        angles, msg = inverse_kinematics(x, y, z)

        if angles:
            j1, j2, j3 = angles

            move_joints(j1, j2, j3)
            time.sleep(1)

            px, py, pz = get_pose()

            print("Target :", x, y, z)
            print("Actual :", round(px,2), round(py,2), round(pz,2))

            error = math.sqrt((px-x)**2 + (py-y)**2 + (pz-z)**2)

        else:
            print("Error:", msg)    

    elif cmd[0] == "fk":
        print("Pose:", get_pose())

    else:
        print("Unknown command")