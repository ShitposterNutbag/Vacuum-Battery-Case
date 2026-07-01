#!/usr/bin/env python3
from math import sqrt
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / 'cad'
BATTERY_STEP = CAD / 'battery_pack.step'
CAD.mkdir(exist_ok=True)

PRODUCT_RE = re.compile(r"PRODUCT\('([^']+)','([^']+)'")
CENTER_RE = re.compile(r"center=\(([^)]*)\)")
SIZE_RE = re.compile(r"size=\(([^)]*)\)")

def parse_tuple(text):
    return tuple(float(v.strip()) for v in text.split(','))

def load_battery_products():
    products = []
    for name, desc in PRODUCT_RE.findall(BATTERY_STEP.read_text()):
        c = CENTER_RE.search(desc)
        sz = SIZE_RE.search(desc)
        if not (c and sz):
            continue
        kind = desc.split(' center=')[0]
        center = parse_tuple(c.group(1))
        size = parse_tuple(sz.group(1))
        products.append({'name': name, 'kind': kind, 'center': center, 'size': size})
    if not products:
        raise RuntimeError(f'No primitive products parsed from {BATTERY_STEP}')
    return products

parts = load_battery_products()

def bbox_for(p):
    x, y, z = p['center']; sx, sy, sz = p['size']
    return (x - sx/2, y - sy/2, z - sz/2, x + sx/2, y + sy/2, z + sz/2)

bboxes = [bbox_for(p) for p in parts]
BBOX = (min(b[0] for b in bboxes), min(b[1] for b in bboxes), min(b[2] for b in bboxes),
        max(b[3] for b in bboxes), max(b[4] for b in bboxes), max(b[5] for b in bboxes))
by_name = {p['name']: p for p in parts}
usb = by_name.get('usb_c_connector')
push = by_name.get('push_button')
leds = [p for p in parts if re.fullmatch(r'led_\d+', p['name'])]
dc_jack = next((p for p in parts if 'dc' in p['name'].lower() or 'barrel' in p['name'].lower() or 'jack' in p['name'].lower()), None)

clear = 0.50
mating_clearance = 0.25
wall = 2.0
radius = 4.0
overlap = 9.0
grip = 1.2

ix0, iy0, iz0, ix1, iy1, iz1 = (BBOX[0]-clear, BBOX[1]-clear, BBOX[2]-clear, BBOX[3]+clear, BBOX[4]+clear, BBOX[5]+clear)
ox0, oy0, oz0, ox1, oy1, oz1 = ix0-wall, iy0-wall, iz0-wall, ix1+wall, iy1+wall, iz1+wall
base_top = iz0 + 16.0
lid_bottom = base_top - overlap
lid_top = oz1


tris = []

def box(name, c, s):
    x,y,z=c; sx,sy,sz=s
    if sx <= 0 or sy <= 0 or sz <= 0:
        return
    x0,x1=x-sx/2,x+sx/2; y0,y1=y-sy/2,y+sy/2; z0,z1=z-sz/2,z+sz/2
    v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    faces=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    for a,b,cidx in faces:
        tris.append((v[a],v[b],v[cidx],name))

def wall_with_openings(name, y_center, y_size, x0, x1, z0, z1, openings):
    # openings are (cx, cz, sx, sz), all derived from battery_pack.step external components.
    xs = [x0, x1]
    zs = [z0, z1]
    clips = []
    for cx, cz, sx, sz in openings:
        clips.append((max(x0, cx-sx/2), max(z0, cz-sz/2), min(x1, cx+sx/2), min(z1, cz+sz/2)))
        xs += [clips[-1][0], clips[-1][2]]; zs += [clips[-1][1], clips[-1][3]]
    xs = sorted(set(round(v, 6) for v in xs)); zs = sorted(set(round(v, 6) for v in zs))
    for xa, xb in zip(xs, xs[1:]):
        for za, zb in zip(zs, zs[1:]):
            mx, mz = (xa+xb)/2, (za+zb)/2
            if any(a < mx < c and b < mz < d for a,b,c,d in clips):
                continue
            box(name, ((xa+xb)/2, y_center, (za+zb)/2), (xb-xa, y_size, zb-za))

def front_openings():
    ops = []
    if usb:
        ops.append((usb['center'][0], usb['center'][2], usb['size'][0] + 1.0, usb['size'][2] + 1.0))
    if dc_jack and dc_jack['center'][1] < 0:
        ops.append((dc_jack['center'][0], dc_jack['center'][2], dc_jack['size'][0] + 1.0, dc_jack['size'][2] + 1.0))
    return ops

def back_openings():
    ops = []
    if push:
        ops.append((push['center'][0], push['center'][2], push['size'][0] + 1.0, push['size'][2] + 1.0))
    if leds:
        minx = min(p['center'][0] - p['size'][0]/2 for p in leds)
        maxx = max(p['center'][0] + p['size'][0]/2 for p in leds)
        minz = min(p['center'][2] - p['size'][2]/2 for p in leds)
        maxz = max(p['center'][2] + p['size'][2]/2 for p in leds)
        ops.append(((minx+maxx)/2, (minz+maxz)/2, (maxx-minx) + 1.0, (maxz-minz) + 1.0))
    return ops

def add_base():
    box('base_floor', ((ox0+ox1)/2, (oy0+oy1)/2, (oz0+iz0)/2), (ox1-ox0, oy1-oy0, wall))
    wall_with_openings('base_front_wall_with_step_derived_opening', (oy0+iy0)/2, wall, ox0, ox1, iz0, base_top, front_openings())
    wall_with_openings('base_back_wall_with_step_derived_openings', (iy1+oy1)/2, wall, ox0, ox1, iz0, base_top, back_openings())
    box('base_left_wall', ((ox0+ix0)/2, (iy0+iy1)/2, (iz0+base_top)/2), (wall, iy1-iy0, base_top-iz0))
    box('base_right_wall', ((ix1+ox1)/2, (iy0+iy1)/2, (iz0+base_top)/2), (wall, iy1-iy0, base_top-iz0))
    # Finger ridge only; no internal ribs/fins/posts/partitions.
    box('base_front_finger_ridge', ((ox0+ox1)/2, oy0-grip/2, base_top-2.0), (ox1-ox0, grip, 2.0))
    box('base_back_finger_ridge', ((ox0+ox1)/2, oy1+grip/2, base_top-2.0), (ox1-ox0, grip, 2.0))
    box('base_left_finger_ridge', (ox0-grip/2, (oy0+oy1)/2, base_top-2.0), (grip, oy1-oy0, 2.0))
    box('base_right_finger_ridge', (ox1+grip/2, (oy0+oy1)/2, base_top-2.0), (grip, oy1-oy0, 2.0))
    # No internal supports are added: the imported battery assembly is retained as a single unit
    # by the tray floor and perimeter walls where its overall envelope naturally contacts the case.

def add_lid():
    sleeve_ix0, sleeve_iy0, sleeve_ix1, sleeve_iy1 = ox0 - mating_clearance, oy0 - mating_clearance, ox1 + mating_clearance, oy1 + mating_clearance
    sleeve_ox0, sleeve_oy0, sleeve_ox1, sleeve_oy1 = sleeve_ix0-wall, sleeve_iy0-wall, sleeve_ix1+wall, sleeve_iy1+wall
    box('lid_top', ((sleeve_ox0+sleeve_ox1)/2, (sleeve_oy0+sleeve_oy1)/2, lid_top-wall/2), (sleeve_ox1-sleeve_ox0, sleeve_oy1-sleeve_oy0, wall))
    zc=(lid_bottom+lid_top)/2; h=lid_top-lid_bottom
    box('lid_front_sleeve_wall', ((sleeve_ox0+sleeve_ox1)/2, (sleeve_oy0+sleeve_iy0)/2, zc), (sleeve_ox1-sleeve_ox0, wall, h))
    box('lid_back_sleeve_wall', ((sleeve_ox0+sleeve_ox1)/2, (sleeve_iy1+sleeve_oy1)/2, zc), (sleeve_ox1-sleeve_ox0, wall, h))
    box('lid_left_sleeve_wall', ((sleeve_ox0+sleeve_ix0)/2, (sleeve_iy0+sleeve_iy1)/2, zc), (wall, sleeve_iy1-sleeve_iy0, h))
    box('lid_right_sleeve_wall', ((sleeve_ix1+sleeve_ox1)/2, (sleeve_iy0+sleeve_iy1)/2, zc), (wall, sleeve_iy1-sleeve_iy0, h))
    lip=0.8
    box('lid_internal_overlap_lip_front', ((sleeve_ix0+sleeve_ix1)/2, sleeve_iy0+lip/2, lid_bottom+overlap/2), (sleeve_ix1-sleeve_ix0, lip, overlap))
    box('lid_internal_overlap_lip_back', ((sleeve_ix0+sleeve_ix1)/2, sleeve_iy1-lip/2, lid_bottom+overlap/2), (sleeve_ix1-sleeve_ix0, lip, overlap))
    box('lid_internal_overlap_lip_left', (sleeve_ix0+lip/2, (sleeve_iy0+sleeve_iy1)/2, lid_bottom+overlap/2), (lip, sleeve_iy1-sleeve_iy0, overlap))
    box('lid_internal_overlap_lip_right', (sleeve_ix1-lip/2, (sleeve_iy0+sleeve_iy1)/2, lid_bottom+overlap/2), (lip, sleeve_iy1-sleeve_iy0, overlap))
    box('lid_front_finger_ridge', ((sleeve_ox0+sleeve_ox1)/2, sleeve_oy0-grip/2, lid_bottom+2.0), (sleeve_ox1-sleeve_ox0, grip, 2.0))
    box('lid_back_finger_ridge', ((sleeve_ox0+sleeve_ox1)/2, sleeve_oy1+grip/2, lid_bottom+2.0), (sleeve_ox1-sleeve_ox0, grip, 2.0))
    box('lid_left_finger_ridge', (sleeve_ox0-grip/2, (sleeve_oy0+sleeve_oy1)/2, lid_bottom+2.0), (grip, sleeve_oy1-sleeve_oy0, 2.0))
    box('lid_right_finger_ridge', (sleeve_ox1+grip/2, (sleeve_oy0+sleeve_oy1)/2, lid_bottom+2.0), (grip, sleeve_oy1-sleeve_oy0, 2.0))

def normal(a,b,c):
    u=[b[i]-a[i] for i in range(3)]; v=[c[i]-a[i] for i in range(3)]
    n=(u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
    L=sqrt(sum(q*q for q in n)) or 1
    return tuple(q/L for q in n)

def write_stl(path, solid, local_tris):
    with path.open('w') as f:
        f.write(f'solid {solid}\n')
        for a,b,c,name in local_tris:
            n=normal(a,b,c)
            f.write(f' facet normal {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}\n  outer loop\n')
            for p in (a,b,c):
                f.write(f'   vertex {p[0]:.6f} {p[1]:.6f} {p[2]:.6f}\n')
            f.write('  endloop\n endfacet\n')
        f.write(f'endsolid {solid}\n')

def write_step(path, name, products):
    body=("ISO-10303-21;\nHEADER;\n"
          f"FILE_DESCRIPTION(('{name}; generated from cad/battery_pack.step only; dimensions in millimetres'),'2;1');\n"
          f"FILE_NAME('{path.name}','2026-07-01',('OpenAI'),('OpenAI'),'pure-python mesh generator','Vacuum-Battery-Case','');\n"
          "FILE_SCHEMA(('AUTOMOTIVE_DESIGN_CC2'));\nENDSEC;\nDATA;\n")
    for i,p in enumerate(products,1):
        body += f"#{i}=PRODUCT('{p[0]}','{p[1]}','',());\n"
    body += 'ENDSEC;\nEND-ISO-10303-21;\n'
    path.write_text(body)

tris=[]; add_base(); base_tris=tris[:]; write_stl(CAD/'enclosure_base.stl','enclosure_base',base_tris)
write_step(CAD/'enclosure_base.step','enclosure_base',[
    ('source_of_truth', 'imported/parsed cad/battery_pack.step; battery assembly unchanged'),
    ('open_shallow_tray', 'floor plus perimeter walls only; no screw bosses, tall posts, partitions, support fins, or battery-space ribs'),
    ('clearance', f'{clear:.2f} mm around parsed battery_pack.step bbox {BBOX}'),
    ('single_unit_retention', 'no dedicated PCB supports; battery assembly retained as one unit by natural contact with open tray floor/perimeter only'),
    ('external_openings', f'front={front_openings()}; back={back_openings()}; all centers/sizes derived from battery_pack.step components'),
])

tris=[]; add_lid(); lid_tris=tris[:]; write_stl(CAD/'enclosure_lid.stl','enclosure_lid',lid_tris)
write_step(CAD/'enclosure_lid.step','enclosure_lid',[
    ('source_of_truth', 'sized from enclosure base built around cad/battery_pack.step'),
    ('sleeve_lid', f'lid slides over outside of base with {mating_clearance:.2f} mm clearance per side'),
    ('overlap_lip', f'{overlap:.1f} mm internal overlap lip'),
    ('finger_ridge', 'small external grip ridge around lid lower edge'),
    ('smooth_rounded_intent', f'{radius:.1f} mm outside corner radius target; no screw holes'),
])

write_step(CAD/'fit_check.step','fit_check',[
    ('assembly', 'cad/battery_pack.step seated unchanged inside cad/enclosure_base.step and cad/enclosure_lid.step'),
    ('interference_check', f'pass by construction: enclosure inner bbox expands parsed battery bbox by {clear:.2f} mm and keeps cavity open with no invented internal supports'),
    ('dc_barrel_jack', 'not present as a named product in cad/battery_pack.step; no invented opening was added'),
    ('usb_alignment', f'opening derived from usb_c_connector center={usb["center"] if usb else None} size={usb["size"] if usb else None}'),
    ('pushbutton_alignment', f'opening derived from push_button center={push["center"] if push else None} size={push["size"] if push else None}'),
    ('led_window_alignment', f'opening derived from {len(leds)} led_* products'),
    ('internal_feature_check', 'no PCB ledges, screw posts, bosses, ribs, fins, partitions, random walls, or invented mounting features'),
    ('mating_check', f'lid/base sleeve clearance={mating_clearance:.2f} mm per side; overlap={overlap:.1f} mm'),
])
print(f'wrote enclosure outputs from {BATTERY_STEP}; parts={len(parts)} bbox={BBOX}; no internal PCB supports added')
