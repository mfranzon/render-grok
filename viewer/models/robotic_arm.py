from build123d import *
from viewer.render import render

# Robotic arm — 6-segment industrial-style manipulator
# Base → shoulder hub → upper arm → elbow → forearm → wrist → end effector + gripper
# All dimensions in mm

# --- Base plate + collar ---
base_plate = Cylinder(50, 12)
base_collar = Pos(0, 0, 12) * Cylinder(30, 20)
base = base_plate + base_collar
base.color = Color("lightslategray")

# --- Shoulder joint hub ---
shoulder_hub = Pos(0, 0, 32) * Sphere(22)
shoulder_hub.color = Color("steelblue")

# --- Upper arm ---
upper_arm = Pos(0, 0, 54) * Box(20, 16, 80, align=(Align.CENTER, Align.CENTER, Align.MIN))
upper_arm = fillet(upper_arm.edges().filter_by(Axis.Z), radius=4)
upper_arm.color = Color("lightslategray")

# --- Elbow joint ---
elbow = Pos(0, 0, 138) * Cylinder(18, 24, align=(Align.CENTER, Align.CENTER, Align.MIN))
elbow.color = Color("steelblue")

# --- Forearm ---
forearm = Pos(0, 0, 162) * Box(16, 14, 70, align=(Align.CENTER, Align.CENTER, Align.MIN))
forearm = fillet(forearm.edges().filter_by(Axis.Z), radius=3)
forearm.color = Color("lightslategray")

# --- Wrist joint ---
wrist = Pos(0, 0, 232) * Sphere(14)
wrist.color = Color("steelblue")

# --- End effector mount ---
ee_mount = Pos(0, 0, 246) * Cylinder(10, 16, align=(Align.CENTER, Align.CENTER, Align.MIN))
ee_mount.color = Color("lightslategray")

# --- Gripper fingers ---
finger_profile = Rectangle(6, 20)
finger_solid = extrude(finger_profile, amount=8)

left_finger = Pos(-12, 0, 262) * finger_solid
right_finger = Pos(12, 0, 262) * finger_solid
left_finger.color = Color("tomato")
right_finger.color = Color("tomato")

# --- Side cables running along the upper arm ---
cable1 = Pos(11, 0, 32) * Cylinder(2, 106, align=(Align.CENTER, Align.CENTER, Align.MIN))
cable2 = Pos(-11, 0, 32) * Cylinder(2, 106, align=(Align.CENTER, Align.CENTER, Align.MIN))
cable1.color = Color("goldenrod")
cable2.color = Color("goldenrod")

arm = Compound(
    children=[
        base,
        shoulder_hub,
        upper_arm,
        elbow,
        forearm,
        wrist,
        ee_mount,
        left_finger,
        right_finger,
        cable1,
        cable2,
    ]
)

render("robotic_arm", arm)
