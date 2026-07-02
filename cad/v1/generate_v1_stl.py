#!/usr/bin/env python3
"""Generate coarse V1 STL exports when OpenSCAD is unavailable."""
from pathlib import Path

battery=(96.7,56.86,55.2); clearance=0.8; wall=2.8; floor=2.8; lid=2.8; split_z=31.0; lip=1.8; post_inset=8; post=7.5
inner=(battery[0]+2*clearance,battery[1]+2*clearance,battery[2]+2*clearance)
outer=(inner[0]+2*wall,inner[1]+2*wall,inner[2]+floor+lid)

def box(name, x0,x1,y0,y1,z0,z1):
    v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    faces=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    return [(name, [v[i] for i in f]) for f in faces]

def write(path, tris):
    with open(path,'w') as f:
        f.write(f"solid {path.stem}\n")
        for _,tri in tris:
            f.write(" facet normal 0 0 0\n  outer loop\n")
            for p in tri: f.write("   vertex %.4f %.4f %.4f\n"%p)
            f.write("  endloop\n endfacet\n")
        f.write(f"endsolid {path.stem}\n")

def bottom():
    ox,oy,_=outer; ix,iy,_=inner; z=floor+split_z
    parts=[]
    parts += box('floor',-ox/2,ox/2,-oy/2,oy/2,0,floor)
    parts += box('left',-ox/2,-ix/2,-oy/2,oy/2,floor,z)
    parts += box('right',ix/2,ox/2,-oy/2,oy/2,floor,z)
    # front wall split around USB cutout
    ux=16; uz0=floor+12; uz1=uz0+9
    for a,b in [(-ix/2,-ux/2),(ux/2,ix/2)]: parts += box('front_x',a,b,-oy/2,-iy/2,floor,z)
    parts += box('front_low',-ux/2,ux/2,-oy/2,-iy/2,floor,uz0)
    parts += box('front_high',-ux/2,ux/2,-oy/2,-iy/2,uz1,z)
    parts += box('back',-ix/2,ix/2,iy/2,oy/2,floor,z)
    for sx in [-1,1]:
      for sy in [-1,1]:
        cx=sx*(ox/2-post_inset); cy=sy*(oy/2-post_inset); parts += box('post',cx-post/2,cx+post/2,cy-post/2,cy+post/2,floor,z-1)
    return parts

def top():
    ox,oy,_=outer; ix,iy,_=inner; z0=floor+split_z; z1=z0+lid
    parts=[]; bx0=-ox/2; bx1=ox/2; by0=-oy/2; by1=oy/2
    # top plate split around button and LED openings
    holes=[(24-7,24+7,-12-7,-12+7),(24-14,24+14,10-3.5,10+3.5)]
    xs=sorted({bx0,bx1,*[h[0] for h in holes],*[h[1] for h in holes]})
    ys=sorted({by0,by1,*[h[2] for h in holes],*[h[3] for h in holes]})
    for xa,xb in zip(xs,xs[1:]):
      for ya,yb in zip(ys,ys[1:]):
        cx=(xa+xb)/2; cy=(ya+yb)/2
        if any(h[0] < cx < h[1] and h[2] < cy < h[3] for h in holes): continue
        parts += box('cap',xa,xb,ya,yb,z0,z1)
    parts += box('lip',-ix/2+.35,ix/2-.35,-iy/2+.35,iy/2-.35,z0-lip,z0)
    for sx in [-1,1]:
      for sy in [-1,1]:
        cx=sx*(ox/2-post_inset); cy=sy*(oy/2-post_inset); parts += box('boss',cx-post/2,cx+post/2,cy-post/2,cy+post/2,z0-lip,z1)
    return parts

out=Path(__file__).parent
write(out/'battery_case_v1_bottom.stl', bottom())
write(out/'battery_case_v1_top.stl', top())
