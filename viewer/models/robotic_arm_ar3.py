from build123d import *
from viewer.render import render

# AR2/AR3-style 6-DOF desktop robotic arm
# Source: reference image (similar to Annin Robotics AR3)
# Total reach ~600mm; lower arm ~320mm, upper arm ~180mm, wrist ~80mm
# Base footprint 160x160mm. All dims in mm.
# Modeled in neutral "arm-straight-up" pose.

DARK   = Color(0.25, 0.27, 0.30)     # dark gray body
GOLD   = Color(0.85, 0.70, 0.15)     # brass standoffs
SILVER = Color(0.62, 0.65, 0.68)     # bearing / accents
CARBON = Color(0.27, 0.29, 0.36)     # carbon fiber tube
YELLOW = Color(0.95, 0.82, 0.10)     # end-effector lens

parts = []

# ── BASE OPEN FRAME ────────────────────────────────────────────────────
# Bottom plate
bp = Box(160, 160, 8)
bp.color = DARK
parts.append(bp)

# 4 gold corner standoff cylinders
for sx in (-1, 1):
    for sy in (-1, 1):
        s = Pos(sx*60, sy*60, 8) * Cylinder(7, 70, align=(Align.CENTER, Align.CENTER, Align.MIN))
        s.color = GOLD
        parts.append(s)

# Top plate (with circular cutout for bearing)
top_box = Pos(0, 0, 78) * Box(160, 160, 8)
top_hole = Pos(0, 0, 74) * Cylinder(52, 16)
top_plate = top_box - top_hole
top_plate.color = DARK
parts.append(top_plate)

# NEMA17 stepper motors — one on each short side of the base
for sy in (-1, 1):
    m_pos = Pos(0, sy * 101, 10)
    motor = m_pos * Box(42, 42, 48, align=(Align.CENTER, Align.MIN if sy < 0 else Align.MAX, Align.MIN))
    motor.color = DARK
    parts.append(motor)
    # Motor shaft
    shaft = m_pos * Cylinder(2.5, 18, align=(Align.CENTER, Align.MIN if sy < 0 else Align.MAX, Align.CENTER))
    shaft = Pos(0, sy * 101 + sy * 27, 34) * Cylinder(2.5, 18, align=(Align.CENTER, Align.CENTER, Align.MIN))
    shaft.color = SILVER
    parts.append(shaft)

# ── SLEW BEARING (turntable) ───────────────────────────────────────────
bear_outer = Pos(0, 0, 86) * Cylinder(52, 22, align=(Align.CENTER, Align.CENTER, Align.MIN))
bear_inner = Pos(0, 0, 84) * Cylinder(34, 28)
bearing = bear_outer - bear_inner
bearing.color = SILVER
parts.append(bearing)

# ── SHOULDER MOTOR BLOCK ───────────────────────────────────────────────
# Main block
sb = Pos(0, 0, 108) * Box(95, 88, 78, align=(Align.CENTER, Align.CENTER, Align.MIN))
# Hollow out interior slightly for visual detail (chamfer-like tray)
sb_cut = Pos(0, 0, 128) * Box(75, 68, 60, align=(Align.CENTER, Align.CENTER, Align.MIN))
shoulder = sb - sb_cut
shoulder.color = DARK
parts.append(shoulder)

# Side bracket extending to rear
side_bkt = Pos(0, -55, 145) * Box(22, 22, 52, align=(Align.CENTER, Align.CENTER, Align.CENTER))
side_bkt.color = DARK
parts.append(side_bkt)

# ── LOWER ARM — 2040 V-slot aluminium extrusion ────────────────────────
# 40mm wide, 20mm deep, 320mm tall
arm_base_z = 186
la = Pos(0, 0, arm_base_z) * Box(40, 20, 320, align=(Align.CENTER, Align.CENTER, Align.MIN))
# V-slot grooves (2 rectangular channels running full length)
g1 = Pos(11, 0, arm_base_z) * Box(3.5, 22, 320, align=(Align.CENTER, Align.CENTER, Align.MIN))
g2 = Pos(-11, 0, arm_base_z) * Box(3.5, 22, 320, align=(Align.CENTER, Align.CENTER, Align.MIN))
lower_arm = la - g1 - g2
lower_arm.color = DARK
parts.append(lower_arm)

# Lower-arm end caps
for z_off in (arm_base_z, arm_base_z + 320):
    cap = Pos(0, 0, z_off) * Box(40, 20, 6, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    cap.color = SILVER
    parts.append(cap)

# ── ELBOW JOINT BLOCK ──────────────────────────────────────────────────
elbow_z = arm_base_z + 320
eb = Pos(0, 0, elbow_z) * Box(62, 52, 52, align=(Align.CENTER, Align.CENTER, Align.MIN))
eb.color = DARK
parts.append(eb)

# Elbow side motor
em = Pos(42, 0, elbow_z + 5) * Box(42, 42, 42, align=(Align.MIN, Align.CENTER, Align.MIN))
em.color = DARK
parts.append(em)

# ── UPPER ARM — carbon fibre round tube ────────────────────────────────
upper_z = elbow_z + 52
tube_out = Pos(0, 0, upper_z) * Cylinder(14, 185, align=(Align.CENTER, Align.CENTER, Align.MIN))
tube_in  = Pos(0, 0, upper_z) * Cylinder(10, 187, align=(Align.CENTER, Align.CENTER, Align.MIN))
upper_arm = tube_out - tube_in
upper_arm.color = CARBON
parts.append(upper_arm)

# End-caps on tube
for z_off in (upper_z, upper_z + 185):
    tc = Pos(0, 0, z_off) * Cylinder(14, 5, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    tc.color = SILVER
    parts.append(tc)

# ── WRIST BLOCK ────────────────────────────────────────────────────────
wrist_z = upper_z + 185
wb = Pos(0, 0, wrist_z) * Box(50, 42, 36, align=(Align.CENTER, Align.CENTER, Align.MIN))
wb.color = DARK
parts.append(wb)

# Wrist rotation hub
wh = Pos(0, 0, wrist_z + 36) * Cylinder(19, 14, align=(Align.CENTER, Align.CENTER, Align.MIN))
wh.color = SILVER
parts.append(wh)

# ── END EFFECTOR ────────────────────────────────────────────────────────
ee_z = wrist_z + 50
ee = Pos(0, 0, ee_z) * Box(44, 38, 28, align=(Align.CENTER, Align.CENTER, Align.MIN))
ee.color = DARK
parts.append(ee)

# Yellow lens / laser
lens = Pos(0, -22, ee_z + 14) * Cylinder(9, 8, align=(Align.CENTER, Align.CENTER, Align.CENTER))
lens.color = YELLOW
parts.append(lens)

# Lens ring
lens_ring = Pos(0, -22, ee_z + 14) * (Cylinder(12, 5) - Cylinder(9, 7))
lens_ring.color = SILVER
parts.append(lens_ring)

arm = Compound(children=parts)
render("robotic_arm_ar3", arm)
