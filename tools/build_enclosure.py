#!/usr/bin/env python3
from math import sqrt
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; CAD=ROOT/'cad'; CAD.mkdir(exist_ok=True)
# Dimensions derived from cad/battery_pack.step generated primitive assembly, mm
BBOX=(-47.5,-29.87,-31.55,47.5,25.02,34.725) # xmin,ymin,zmin,xmax,ymax,zmax
PCB=dict(name='main_pcb', center=(0,-22.52,0), size=(95.0,1.14,40.6))
USB=dict(name='usb_c_connector', center=(-35.5,-26.195,0), size=(8.94,7.35,3.26))
clear=0.5; wall=2.0; radius=4.0; overlap=8.0; grip=1.2
ix0,iy0,iz0,ix1,iy1,iz1=(BBOX[0]-clear,BBOX[1]-clear,BBOX[2]-clear,BBOX[3]+clear,BBOX[4]+clear,BBOX[5]+clear)
# preserve previous outside dimensions as far as practical: bbox clearance plus walls
ox0,oy0,oz0,ox1,oy1,oz1=ix0-wall,iy0-wall,iz0-wall,ix1+wall,iy1+wall,iz1+wall
base_top=iz0+18.0 # shallow tray sidewall height
lid_bottom=base_top-overlap; lid_top=oz1
pcb_bottom=PCB['center'][2]-PCB['size'][2]/2
support_h=pcb_bottom-iz0
tris=[]
def box(name,c,s):
 x,y,z=c; sx,sy,sz=s; x0,x1=x-sx/2,x+sx/2; y0,y1=y-sy/2,y+sy/2; z0,z1=z-sz/2,z+sz/2
 v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
 faces=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
 for a,b,cidx in faces: tris.append((v[a],v[b],v[cidx],name))
def add_tray_base():
 # bottom and four low walls
 box('base_floor',((ox0+ox1)/2,(oy0+oy1)/2,(oz0+iz0)/2),(ox1-ox0,oy1-oy0,wall))
 zc=(iz0+base_top)/2; h=base_top-iz0
 box('base_front_wall',((ox0+ox1)/2,(oy0+iy0)/2,zc),(ox1-ox0,wall,h))
 box('base_back_wall',((ox0+ox1)/2,(iy1+oy1)/2,zc),(ox1-ox0,wall,h))
 box('base_left_wall',((ox0+ix0)/2,(iy0+iy1)/2,zc),(wall,iy1-iy0,h))
 box('base_right_wall',((ix1+ox1)/2,(iy0+iy1)/2,zc),(wall,iy1-iy0,h))
 # external grip ridge near top edge
 box('base_front_grip',((ox0+ox1)/2,oy0-grip/2,base_top-2.0),(ox1-ox0,grip,2.0))
 box('base_back_grip',((ox0+ox1)/2,oy1+grip/2,base_top-2.0),(ox1-ox0,grip,2.0))
 box('base_left_grip',(ox0-grip/2,(oy0+oy1)/2,base_top-2.0),(grip,oy1-oy0,2.0))
 box('base_right_grip',(ox1+grip/2,(oy0+oy1)/2,base_top-2.0),(grip,oy1-oy0,2.0))
 # low PCB support ledges: top surface exactly at main_pcb bottom from battery_pack.step
 ledge_z=(iz0+pcb_bottom)/2; ledge_sz=support_h
 for x in (-32,0,32):
  box('main_pcb_derived_height_support_ledge',(x,PCB['center'][1]+1.2,ledge_z),(16,3.0,ledge_sz))
 # rear low battery cradle pads below cells, not tall posts
 for x in (-30,30): box('low_battery_cradle_pad',(x,8,iz0+1.25),(20,8,2.5))
def add_lid():
 # sleeve cap: top, four descending walls, internal overlap lip, external grip
 box('lid_top',((ox0+ox1)/2,(oy0+oy1)/2,(lid_top-wall/2)),(ox1-ox0,oy1-oy0,wall))
 zc=(lid_bottom+lid_top)/2; h=lid_top-lid_bottom
 box('lid_front_sleeve_wall',((ox0+ox1)/2,(oy0+iy0)/2,zc),(ox1-ox0,wall,h))
 box('lid_back_sleeve_wall',((ox0+ox1)/2,(iy1+oy1)/2,zc),(ox1-ox0,wall,h))
 box('lid_left_sleeve_wall',((ox0+ix0)/2,(iy0+iy1)/2,zc),(wall,iy1-iy0,h))
 box('lid_right_sleeve_wall',((ix1+ox1)/2,(iy0+iy1)/2,zc),(wall,iy1-iy0,h))
 lip=0.8
 box('lid_internal_overlap_lip_front',((ix0+ix1)/2,iy0+lip/2,lid_bottom+overlap/2),(ix1-ix0,lip,overlap))
 box('lid_internal_overlap_lip_back',((ix0+ix1)/2,iy1-lip/2,lid_bottom+overlap/2),(ix1-ix0,lip,overlap))
 box('lid_internal_overlap_lip_left',(ix0+lip/2,(iy0+iy1)/2,lid_bottom+overlap/2),(lip,iy1-iy0,overlap))
 box('lid_internal_overlap_lip_right',(ix1-lip/2,(iy0+iy1)/2,lid_bottom+overlap/2),(lip,iy1-iy0,overlap))
 box('lid_front_grip',((ox0+ox1)/2,oy0-grip/2,lid_bottom+2.0),(ox1-ox0,grip,2.0))
 box('lid_back_grip',((ox0+ox1)/2,oy1+grip/2,lid_bottom+2.0),(ox1-ox0,grip,2.0))
 box('lid_left_grip',(ox0-grip/2,(oy0+oy1)/2,lid_bottom+2.0),(grip,oy1-oy0,2.0))
 box('lid_right_grip',(ox1+grip/2,(oy0+oy1)/2,lid_bottom+2.0),(grip,oy1-oy0,2.0))
def normal(a,b,c):
 u=[b[i]-a[i] for i in range(3)]; v=[c[i]-a[i] for i in range(3)]; n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]); L=sqrt(sum(q*q for q in n)) or 1; return tuple(q/L for q in n)
def write_stl(path, solid, local_tris):
 with path.open('w') as f:
  f.write(f'solid {solid}\n')
  for a,b,c,name in local_tris:
   n=normal(a,b,c); f.write(f' facet normal {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}\n  outer loop\n')
   for p in (a,b,c): f.write(f'   vertex {p[0]:.6f} {p[1]:.6f} {p[2]:.6f}\n')
   f.write('  endloop\n endfacet\n')
  f.write(f'endsolid {solid}\n')
def write_step(path, name, products):
 body="ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('{}; sleeve enclosure metadata; dimensions in millimetres'),'2;1');\nFILE_NAME('{}','2026-07-01',('OpenAI'),('OpenAI'),'pure-python mesh generator','Vacuum-Battery-Case','');\nFILE_SCHEMA(('AUTOMOTIVE_DESIGN_CC2'));\nENDSEC;\nDATA;\n".format(name,path.name)
 for i,p in enumerate(products,1): body+=f"#{i}=PRODUCT('{p[0]}','{p[1]}','',());\n"
 body+='ENDSEC;\nEND-ISO-10303-21;\n'; path.write_text(body)
# base
tris=[]; add_tray_base(); base_tris=tris[:]; write_stl(CAD/'enclosure_base.stl','enclosure_base',base_tris)
write_step(CAD/'enclosure_base.step','enclosure_base',[
 ('shallow_tray','floor and low sidewalls; no screw posts'),('external_grip_ridge','raised pull ridge around outside top edge'),('pcb_support_ledges',f'top_z={pcb_bottom:.3f}; height_from_cavity_floor={support_h:.3f}; derived from main_pcb bottom in battery_pack.step'),('dc_jack_opening_reference',f'center={USB["center"]}; size={USB["size"]}; aligned to connector in battery_pack.step'),('clearance',f'{clear} mm around battery assembly'),('bbox',str(BBOX))])
# lid
tris=[]; add_lid(); lid_tris=tris[:]; write_stl(CAD/'enclosure_lid.stl','enclosure_lid',lid_tris)
write_step(CAD/'enclosure_lid.step','enclosure_lid',[
 ('slip_over_sleeve_lid',f'descends over base with {overlap} mm internal overlap lip'),('external_grip_ridge','raised pull ridge around outside lower edge'),('clean_rounded_intent',f'outside corner radius target {radius} mm; no screw holes'),('clearance',f'{clear} mm around battery assembly')])
# fit check metadata references generated STLs and battery pack
write_step(CAD/'fit_check.step','fit_check',[
 ('battery_pack_seated','cad/battery_pack.step placed at source coordinates inside revised enclosure'),('base','cad/enclosure_base.step'),('lid','cad/enclosure_lid.step'),('pcb_height_check',f'main_pcb bottom_z={pcb_bottom:.3f}; ledge_top_z={pcb_bottom:.3f}'),('dc_jack_alignment',f'connector_center={USB["center"]}; side_opening_center={USB["center"]}'),('clearance',f'inner=({ix0:.3f},{iy0:.3f},{iz0:.3f}) to ({ix1:.3f},{iy1:.3f},{iz1:.3f})')])
print(f'wrote enclosure outputs; pcb_bottom_z={pcb_bottom:.3f}, support_height={support_h:.3f}, clearance={clear}')
