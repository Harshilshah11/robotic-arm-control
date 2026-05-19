# --- Step 2: Simulation ---
import pybullet as p
import time

p.connect(p.GUI)
p.setGravity(0, 0, -9.81)

p.setAdditionalSearchPath(
    r"C:/Users/Harshil/Desktop/Robotic arm/simulation/niryoone"
)

urdf_path = r"C:/Users/Harshil/Desktop/Robotic arm/simulation/niryoone/niryoone_fixed.urdf"

robot_id = p.loadURDF(
    urdf_path,
    [0, 0, 0],
    p.getQuaternionFromEuler([0, 0, 0]),
    useFixedBase=True
)

print("Robot loaded! Joint count:", p.getNumJoints(robot_id))

while True:
    p.stepSimulation()
    time.sleep(1./240.)