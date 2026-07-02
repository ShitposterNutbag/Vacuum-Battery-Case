#!/usr/bin/env python3
"""Generate the V2 bottom STL from the same dimensions used by battery_case_v2.scad."""
from pathlib import Path

battery = (96.7, 56.86, 55.2)
clearance = 0.8
wall = 2.8
floor = 2.0
bottom_height = 31.0 + floor
rail_width = 3.0
rail_inset = 12.0
rail_height = 9.5
jack_width = 9.5
jack_height = 7.5

inner = (battery[0] + 2 * clearance, battery[1] + 2 * clearance, battery[2] + 2 * clearance)
outer = (inner[0] + 2 * wall, inner[1] + 2 * wall, inner[2] + floor + 2.8)
case_length, case_width = outer[0], outer[1]

triangles = []

def add_box(name, x0, x1, y0, y1, z0, z1):
    v = {
        '000': (x0, y0, z0), '100': (x1, y0, z0), '110': (x1, y1, z0), '010': (x0, y1, z0),
        '001': (x0, y0, z1), '101': (x1, y0, z1), '111': (x1, y1, z1), '011': (x0, y1, z1),
    }
    faces = [
        ('bottom', '000','110','100', '000','010','110'), ('top', '001','101','111', '001','111','011'),
        ('front', '000','100','101', '000','101','001'), ('back', '010','011','111', '010','111','110'),
        ('left', '000','001','011', '000','011','010'), ('right', '100','110','111', '100','111','101'),
    ]
    for _, a,b,c, d,e,f in faces:
        triangles.append((name, v[a], v[b], v[c])); triangles.append((name, v[d], v[e], v[f]))

x0, x1 = -case_length/2, case_length/2
y0, y1 = -case_width/2, case_width/2
ix0, ix1 = -inner[0]/2, inner[0]/2
iy0, iy1 = -inner[1]/2, inner[1]/2
# floor and long side walls
add_box('floor', x0, x1, y0, y1, 0, floor)
add_box('long_wall_neg_y', x0, x1, y0, iy0, floor, bottom_height)
add_box('long_wall_pos_y', x0, x1, iy1, y1, floor, bottom_height)
# +X short wall (solid)
add_box('short_wall_pos_x', ix1, x1, iy0, iy1, floor, bottom_height)
# -X short wall with centered DC jack opening from Z=floor to floor+jack_height
sx0, sx1 = x0, ix0
jy0, jy1 = -jack_width/2, jack_width/2
jz1 = floor + jack_height
add_box('short_wall_neg_x_left_of_jack', sx0, sx1, iy0, jy0, floor, bottom_height)
add_box('short_wall_neg_x_right_of_jack', sx0, sx1, jy1, iy1, floor, bottom_height)
add_box('short_wall_neg_x_above_jack', sx0, sx1, jy0, jy1, jz1, bottom_height)
# two full internal length rails, inset from side walls
for sign in (-1, 1):
    y = sign * (inner[1]/2 - rail_inset)
    add_box(f'rail_{sign}', ix0, ix1, y - rail_width/2, y + rail_width/2, floor, floor + rail_height)

out = Path(__file__).with_name('battery_case_v2_bottom.stl')
with out.open('w', encoding='utf-8') as f:
    f.write('solid battery_case_v2_bottom\n')
    for name, a, b, c in triangles:
        f.write(f'  facet normal 0 0 0 // {name}\n    outer loop\n')
        for p in (a, b, c):
            f.write(f'      vertex {p[0]:.4f} {p[1]:.4f} {p[2]:.4f}\n')
        f.write('    endloop\n  endfacet\n')
    f.write('endsolid battery_case_v2_bottom\n')
print(out)
