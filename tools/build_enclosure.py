#!/usr/bin/env python3
from __future__ import annotations
import re
from math import sqrt
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; CAD=ROOT/'cad'
STEP_IN=CAD/'battery_pack.step'
PRODUCT_RE=re.compile(r"PRODUCT\('([^']+)','([^']*)'")
CS_RE=re.compile(r"(box|cylinder_[xyz]) center=\(([^)]*)\) size=\(([^)]*)\)")
def nums(s): return tuple(float(p.strip()) for p in s.split(','))
def read_parts():
 parts=[]
 for line in STEP_IN.read_text().splitlines():
  m=PRODUCT_RE.search(line)
  if not m: continue
  cm=CS_RE.search(m.group(2))
  if cm: parts.append({'name':m.group(1),'kind':cm.group(1),'center':nums(cm.group(2)),'size':nums(cm.group(3))})
 return parts
parts=read_parts()
if not parts: raise SystemExit('no primitive products found in cad/battery_pack.step')
def bounds(ps):
 xs=[]; ys=[]; zs=[]
 for p in ps:
  x,y,z=p['center']; sx,sy,sz=p['size']
  xs += [x-sx/2,x+sx/2]; ys += [y-sy/2,y+sy/2]; zs += [z-sz/2,z+sz/2]
 return min(xs),min(ys),min(zs),max(xs),max(ys),max(zs)
BBOX=bounds(parts)
part={p['name']:p for p in parts}
clear=0.5; slide=0.25; wall=2.0; overlap=9.0; grip=0.9
ix0,iy0,iz0,ix1,iy1,iz1=(BBOX[0]-clear,BBOX[1]-clear,BBOX[2]-clear,BBOX[3]+clear,BBOX[4]+clear,BBOX[5]+clear)
base_outer=(ix0-wall,iy0-wall,iz0-wall,ix1+wall,iy1+wall,iz1+wall)
ox0,oy0,oz0,ox1,oy1,oz1=base_outer
base_top=iz0+16.0                         # shallow tray, below pack mid-height
lid_inner=(ox0-slide,oy0-slide,base_top-overlap,ox1+slide,oy1+slide,oz1)
lx0,ly0,lz0,lx1,ly1,lz1=(lid_inner[0]-wall,lid_inner[1]-wall,lid_inner[2],lid_inner[3]+wall,lid_inner[4]+wall,lid_inner[5]+wall)
tris=[]
def box(name,c,s):
 x,y,z=c; sx,sy,sz=s
 if min(s)<=0: return
 x0,x1=x-sx/2,x+sx/2; y0,y1=y-sy/2,y+sy/2; z0,z1=z-sz/2,z+sz/2
 v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
 faces=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
 for a,b,cidx in faces: tris.append((v[a],v[b],v[cidx],name))
def wall_with_rect_openings(prefix,yc,x0,x1,z0,z1,t,openings):
 # front/back wall split into rectangular patches around openings (x,z rectangles)
 xs=sorted({x0,x1,*[o[0] for o in openings],*[o[1] for o in openings]})
 zs=sorted({z0,z1,*[o[2] for o in openings],*[o[3] for o in openings]})
 for xa,xb in zip(xs,xs[1:]):
  for za,zb in zip(zs,zs[1:]):
   cx=(xa+xb)/2; cz=(za+zb)/2
   if any(oa<cx<ob and oc<cz<od for oa,ob,oc,od,_ in openings): continue
   box(prefix,(cx,yc,cz),(xb-xa,t,zb-za))
def opening_for(name,zmin,zmax,margin=1.0):
 p=part.get(name)
 if not p: return None
 x,y,z=p['center']; sx,sy,sz=p['size']
 za=max(zmin,z-sz/2-margin); zb=min(zmax,z+sz/2+margin)
 if za>=zb: return None
 return (max(ox0,x-sx/2-margin),min(ox1,x+sx/2+margin),za,zb,name)
def openings_for_range(zmin,zmax):
 front=[o for o in [opening_for('usb_c_connector',zmin,zmax,1.0)] if o]
 back=[]
 btn=opening_for('push_button',zmin,zmax,1.5)
 if btn: back.append(btn)
 leds=[p for p in parts if p['name'].startswith('led_')]
 if leds:
  lb=bounds(leds); za=max(zmin,lb[2]-1.0); zb=min(zmax,lb[5]+1.0)
  if za<zb: back.append((lb[0]-1.0,lb[3]+1.0,za,zb,'led_window'))
 return front,back
front_open,back_open=openings_for_range(iz0,base_top)
def build_base():
 box('base_floor',((ox0+ox1)/2,(oy0+oy1)/2,(oz0+iz0)/2),(ox1-ox0,oy1-oy0,wall))
 zc=(iz0+base_top)/2; h=base_top-iz0
 wall_with_rect_openings('base_front_wall', (oy0+iy0)/2, ox0, ox1, iz0, base_top, wall, front_open)
 wall_with_rect_openings('base_back_wall', (iy1+oy1)/2, ox0, ox1, iz0, base_top, wall, back_open)
 box('base_left_wall',((ox0+ix0)/2,(iy0+iy1)/2,zc),(wall,iy1-iy0,h))
 box('base_right_wall',((ix1+ox1)/2,(iy0+iy1)/2,zc),(wall,iy1-iy0,h))
 # low, open cradle ledges only: short pads under holder rails/cell carrier, not PCB posts.
 for x in (-24,24):
  box('low_open_cradle_pad',(x,0,iz0+1.0),(28,34,2.0))
 # small pull ridges outside lower tray edges
 for z in (base_top-2.0,):
  box('base_front_grip',((ox0+ox1)/2,oy0-grip/2,z),(50,grip,1.5)); box('base_back_grip',((ox0+ox1)/2,oy1+grip/2,z),(50,grip,1.5))
def build_lid():
 box('lid_top',((lx0+lx1)/2,(ly0+ly1)/2,lz1-wall/2),(lx1-lx0,ly1-ly0,wall))
 zc=(lz0+lz1-wall)/2; h=lz1-wall-lz0
 lid_front_open,lid_back_open=openings_for_range(lz0,lz1-wall)
 wall_with_rect_openings('lid_front_sleeve_wall',(ly0+oy0-slide)/2,lx0,lx1,lz0,lz1-wall,wall,lid_front_open)
 wall_with_rect_openings('lid_back_sleeve_wall',(oy1+slide+ly1)/2,lx0,lx1,lz0,lz1-wall,wall,lid_back_open)
 box('lid_left_sleeve_wall',((lx0+ox0-slide)/2,(oy0+oy1)/2,zc),(wall,oy1-oy0+2*slide,h))
 box('lid_right_sleeve_wall',((ox1+slide+lx1)/2,(oy0+oy1)/2,zc),(wall,oy1-oy0+2*slide,h))
 # external grip ridges near lid skirt bottom
 box('lid_front_grip',((lx0+lx1)/2,ly0-grip/2,lz0+2.0),(50,grip,1.5)); box('lid_back_grip',((lx0+lx1)/2,ly1+grip/2,lz0+2.0),(50,grip,1.5))
def normal(a,b,c):
 u=[b[i]-a[i] for i in range(3)]; v=[c[i]-a[i] for i in range(3)]; n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]); L=sqrt(sum(q*q for q in n)) or 1; return tuple(q/L for q in n)
def write_stl(path,solid,local):
 with path.open('w') as f:
  f.write(f'solid {solid}\n')
  for a,b,c,name in local:
   n=normal(a,b,c); f.write(f' facet normal {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}\n  outer loop\n')
   for p in (a,b,c): f.write(f'   vertex {p[0]:.6f} {p[1]:.6f} {p[2]:.6f}\n')
   f.write('  endloop\n endfacet\n')
  f.write(f'endsolid {solid}\n')
def write_step(path,name,products):
 body="ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('{}; generated from cad/battery_pack.step primitive products; dimensions in millimetres'),'2;1');\nFILE_NAME('{}','2026-07-01',('OpenAI'),('OpenAI'),'pure-python mesh generator','Vacuum-Battery-Case','');\nFILE_SCHEMA(('AUTOMOTIVE_DESIGN_CC2'));\nENDSEC;\nDATA;\n".format(name,path.name)
 for i,p in enumerate(products,1): body+=f"#{i}=PRODUCT('{p[0]}','{p[1]}','',());\n"
 body+='ENDSEC;\nEND-ISO-10303-21;\n'; path.write_text(body)
tris=[]; build_base(); base=tris[:]; write_stl(CAD/'enclosure_base.stl','enclosure_base',base)
write_step(CAD/'enclosure_base.step','enclosure_base',[('source','cad/battery_pack.step parsed as single fixed battery assembly'),('clearance',f'assembly clearance {clear} mm; wall {wall} mm'),('sleeve_overlap',f'{overlap} mm; lid/base sliding clearance {slide} mm per side'),('openings',f'base front={front_open}; base back={back_open}; lid front/back openings are generated from the same source products; no dc barrel jack product found in source STEP'),('supports','two low open cradle pads only; no screw bosses, posts, ribs, fins, partitions, or text')])
tris=[]; build_lid(); lid=tris[:]; write_stl(CAD/'enclosure_lid.stl','enclosure_lid',lid)
write_step(CAD/'enclosure_lid.step','enclosure_lid',[('source','sliding sleeve lid sized from parsed battery assembly envelope'),('clearance',f'lid inner clears base outer by {slide} mm per side'),('overlap',f'{overlap} mm over shallow tray'),('features','outside pull ridges and rounded-corner design intent only; no logo or text')])
write_step(CAD/'fit_check.step','fit_check',[('battery_assembly','cad/battery_pack.step at original coordinates, kept as one fixed unit'),('base','cad/enclosure_base.step'),('lid','cad/enclosure_lid.step'),('assembly_bbox',str(BBOX)),('inner_clearance_bbox',f'{(ix0,iy0,iz0,ix1,iy1,iz1)}'),('openings',f'located from source products; base front={front_open}; base back={back_open}; lid carries any openings above tray height')])
print(f'wrote revised sleeve enclosure from {len(parts)} source STEP products; bbox={BBOX}')
