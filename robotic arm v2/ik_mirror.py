import math

# Exact values from your Pico code
l1 = 18
l2 = 21
l3 = 35

def solve_ik(x_cm, y_cm, z_cm):
    """
    Returns (base_deg, shoulder_deg, elbow_deg) or None if unreachable
    x_cm = left/right from base center
    y_cm = forward distance
    z_cm = height above base
    """
    # Joint 1: base rotation
    base_deg = math.degrees(math.atan2(x_cm, y_cm))

    # Horizontal reach
    r = math.sqrt(x_cm**2 + y_cm**2)
    D = math.sqrt(r**2 + z_cm**2)

    if D > (l1 + l2) or D < abs(l1 - l2):
        print(f"  [IK] Unreachable! D={D:.1f} max={l1+l2}")
        return None

    # Shoulder
    alpha    = math.degrees(math.atan2(z_cm, r))
    cos_beta = (D**2 + l1**2 - l2**2) / (2 * D * l1)
    cos_beta = max(-1.0, min(1.0, cos_beta))
    beta     = math.degrees(math.acos(cos_beta))
    shoulder_deg = alpha + beta

    # Elbow
    cos_e    = (l1**2 + l2**2 - D**2) / (2 * l1 * l2)
    cos_e    = max(-1.0, min(1.0, cos_e))
    elbow_deg = math.degrees(math.acos(cos_e)) - 180

    # Clamp to your joint limits from Pico code
    base_deg     = max(-175, min(175, base_deg))
    shoulder_deg = max(-20,  min(70,  shoulder_deg))
    elbow_deg    = max(-90,  min(80,  elbow_deg))

    print(f"  [IK] base={base_deg:.1f} shoulder={shoulder_deg:.1f} elbow={elbow_deg:.1f}")
    return base_deg, shoulder_deg, elbow_deg