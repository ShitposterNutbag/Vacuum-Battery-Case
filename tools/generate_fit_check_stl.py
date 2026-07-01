#!/usr/bin/env python3
"""Generate a printable fit-check STL enclosure from the committed GLB scan bbox.
No third-party packages are required; CadQuery source with equivalent parameters is in cad/.
"""
from __future__ import annotations
import json, struct, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN = ROOT / '6_30_2026.glb'
OUT = ROOT / 'output' / 'vacuum_battery_fit_check_enclosure.stl'

SCALE_MM_PER_SCAN_UNIT = 50.0
WALL = 2.4
FLOOR = 2.8
CLEARANCE = 1.5
MIN_INTERNAL_HEIGHT = 32.0
LIP_HEIGHT = 3.0
LIP_WALL = 1.2
CORNER_POST = 6.0

# Cutout dimensions/locations are intentionally parametric and visible in cad/vacuum_battery_case.py.
USB_C = dict(width=10.5, height=4.2, z_offset=10.0)
CHARGE_MODULE = dict(width=28.0, height=12.0, z_offset=18.0)
SWITCH = dict(width=14.0, height=7.0, x_offset=26.0)
LED = dict(diameter=3.2, spacing=7.0, count=4, x_offset=-18.0)


def scan_bbox(path: Path):
    data = path.read_bytes()
    magic, version, length = struct.unpack_from('<III', data, 0)
    if magic != 0x46546C67 or version != 2:
        raise ValueError(f'{path} is not a GLB v2 file')
    off = 12
    mins, maxs = [], []
    while off < len(data):
        clen, ctype = struct.unpack_from('<II', data, off); off += 8
        chunk = data[off:off+clen]; off += clen
        if ctype == 0x4E4F534A:
            doc = json.loads(chunk.decode('utf-8'))
            for acc in doc.get('accessors', []):
                if acc.get('type') == 'VEC3' and 'min' in acc and 'max' in acc:
                    mins.append(acc['min']); maxs.append(acc['max'])
    return [min(v[i] for v in mins) for i in range(3)], [max(v[i] for v in maxs) for i in range(3)]


def box_triangles(cx, cy, cz, sx, sy, sz):
    x0,x1 = cx-sx/2, cx+sx/2; y0,y1 = cy-sy/2, cy+sy/2; z0,z1 = cz-sz/2, cz+sz/2
    v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    faces=[(0,1,2),(0,2,3),(4,6,5),(4,7,6),(0,4,5),(0,5,1),(1,5,6),(1,6,2),(2,6,7),(2,7,3),(3,7,4),(3,4,0)]
    return [(v[a],v[b],v[c]) for a,b,c in faces]


def add_panel_with_cutouts(tris, panel, axis, pos, length, height, thick, cutouts):
    # axis 'z': front/back panel spans X/Y at constant Z. cutouts are (cx, cy, w, h).
    intervals_y = [(-height/2, height/2)]
    for _, cy, _, h in cutouts:
        new=[]
        for a,b in intervals_y:
            if cy-h/2>a: new.append((a, min(b, cy-h/2)))
            if cy+h/2<b: new.append((max(a, cy+h/2), b))
        intervals_y=[p for p in new if p[1]-p[0]>.1]
    for ya,yb in intervals_y:
        xs=[-length/2]
        for cx, cy, w, h in cutouts:
            if not (yb <= cy-h/2 or ya >= cy+h/2): xs += [cx-w/2, cx+w/2]
        xs += [length/2]; xs=sorted(xs)
        for xa,xb in zip(xs,xs[1:]):
            blocked=any(xa>=cx-w/2-.01 and xb<=cx+w/2+.01 and not (yb<=cy-h/2 or ya>=cy+h/2) for cx,cy,w,h in cutouts)
            if not blocked and xb-xa>.1:
                cx=(xa+xb)/2; cy=(ya+yb)/2
                if axis=='z': tris += box_triangles(cx, cy, pos, xb-xa, yb-ya, thick)
                else: tris += box_triangles(pos, cy, cx, thick, yb-ya, xb-xa)


def write_stl(tris, path):
    def normal(a,b,c):
        ux,uy,uz=[b[i]-a[i] for i in range(3)]; vx,vy,vz=[c[i]-a[i] for i in range(3)]
        n=(uy*vz-uz*vy, uz*vx-ux*vz, ux*vy-uy*vx); l=math.sqrt(sum(i*i for i in n)) or 1
        return tuple(i/l for i in n)
    with path.open('w') as f:
        f.write('solid vacuum_battery_fit_check_enclosure\n')
        for a,b,c in tris:
            n=normal(a,b,c); f.write(f' facet normal {n[0]:.6g} {n[1]:.6g} {n[2]:.6g}\n  outer loop\n')
            for p in (a,b,c): f.write(f'   vertex {p[0]:.6g} {p[1]:.6g} {p[2]:.6g}\n')
            f.write('  endloop\n endfacet\n')
        f.write('endsolid vacuum_battery_fit_check_enclosure\n')


def main():
    mn,mx=scan_bbox(SCAN)
    scan_x=(mx[0]-mn[0])*SCALE_MM_PER_SCAN_UNIT; scan_z=(mx[2]-mn[2])*SCALE_MM_PER_SCAN_UNIT; scan_y=(mx[1]-mn[1])*SCALE_MM_PER_SCAN_UNIT
    inner_x=scan_x+2*CLEARANCE; inner_z=scan_z+2*CLEARANCE; inner_y=max(scan_y+2*CLEARANCE, MIN_INTERNAL_HEIGHT)
    outer_x=inner_x+2*WALL; outer_z=inner_z+2*WALL; outer_y=inner_y+FLOOR
    tris=[]
    tris += box_triangles(0, FLOOR/2, 0, outer_x, FLOOR, outer_z) # floor
    # side walls, with front cutouts split around apertures
    add_panel_with_cutouts(tris, 'front','z', -outer_z/2+WALL/2, outer_x, inner_y, WALL,
        [(0, FLOOR+USB_C['z_offset'], USB_C['width'], USB_C['height']), (0, FLOOR+CHARGE_MODULE['z_offset'], CHARGE_MODULE['width'], CHARGE_MODULE['height'])])
    tris += box_triangles(0, FLOOR+inner_y/2, outer_z/2-WALL/2, outer_x, inner_y, WALL)
    add_panel_with_cutouts(tris, 'left','x', -outer_x/2+WALL/2, outer_z, inner_y, WALL, [])
    add_panel_with_cutouts(tris, 'right','x', outer_x/2-WALL/2, outer_z, inner_y, WALL,
        [(SWITCH['x_offset'], FLOOR+inner_y*.55, SWITCH['width'], SWITCH['height'])])
    # raised locator lip and corner posts
    tris += box_triangles(0, outer_y+LIP_HEIGHT/2, -inner_z/2, inner_x, LIP_HEIGHT, LIP_WALL)
    tris += box_triangles(0, outer_y+LIP_HEIGHT/2, inner_z/2, inner_x, LIP_HEIGHT, LIP_WALL)
    tris += box_triangles(-inner_x/2, outer_y+LIP_HEIGHT/2, 0, LIP_WALL, LIP_HEIGHT, inner_z)
    tris += box_triangles(inner_x/2, outer_y+LIP_HEIGHT/2, 0, LIP_WALL, LIP_HEIGHT, inner_z)
    for sx in (-1,1):
        for sz in (-1,1): tris += box_triangles(sx*(inner_x/2-CORNER_POST/2), FLOOR+inner_y/2, sz*(inner_z/2-CORNER_POST/2), CORNER_POST, inner_y, CORNER_POST)
    # LED drill guide bosses on top front rail (shallow marks, drill through after print)
    for i in range(LED['count']):
        x=LED['x_offset']+(i-(LED['count']-1)/2)*LED['spacing']
        tris += box_triangles(x, outer_y+0.6, -outer_z/2+WALL+6, LED['diameter'], 1.2, LED['diameter'])
    OUT.parent.mkdir(exist_ok=True)
    write_stl(tris, OUT)
    print(f'wrote {OUT} ({outer_x:.1f} x {outer_z:.1f} x {outer_y+LIP_HEIGHT:.1f} mm), scan bbox mm {scan_x:.1f} x {scan_z:.1f} x {scan_y:.1f}')

if __name__=='__main__': main()
