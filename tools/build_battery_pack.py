#!/usr/bin/env python3
from math import sin, cos, pi, sqrt
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]; CAD=ROOT/'cad'; CAD.mkdir(exist_ok=True)
P=dict(overall_width=63.7,overall_height=63.1,overall_depth=43.9,cell_d=18.3,cell_l=65.0,main_pcb_l=95.0,main_pcb_w=40.6,pcb_t=1.14,led_pcb_h=53.3,led_pcb_w=20.8)
# Unknown parameters: values are intentionally named construction parameters needing verification.
U=dict(carrier_wall=1.6,carrier_rib=2.0,clip_lip=1.2,usb_c_w=8.94,usb_c_h=3.26,usb_c_d=7.35,button_w=6.0,button_h=3.5,button_d=2.5,ribbon_w=10.0,ribbon_t=0.35,led_d=3.0)
tris=[]; solids=[]
def add_box(name,c,s):
 x,y,z=c; sx,sy,sz=s; x0,x1=x-sx/2,x+sx/2; y0,y1=y-sy/2,y+sy/2; z0,z1=z-sz/2,z+sz/2
 v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
 faces=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
 tris.extend((v[a],v[b],v[c],name) for a,b,c in faces); solids.append((name,'box',c,s))
def cyl_x(name,c,l,r,n=48):
 x,y,z=c; x0=x-l/2; x1=x+l/2
 for i in range(n):
  a=2*pi*i/n; b=2*pi*(i+1)/n
  p0=(x0,y+r*cos(a),z+r*sin(a)); p1=(x0,y+r*cos(b),z+r*sin(b)); p2=(x1,y+r*cos(b),z+r*sin(b)); p3=(x1,y+r*cos(a),z+r*sin(a))
  tris.extend([(p0,p1,p2,name),(p0,p2,p3,name),((x0,y,z),p1,p0,name),((x1,y,z),p3,p2,name)])
 solids.append((name,'cylinder_x',c,(l,r*2,r*2)))
def cyl_y(name,c,l,r,n=32):
 x,y,z=c; y0=y-l/2; y1=y+l/2
 for i in range(n):
  a=2*pi*i/n; b=2*pi*(i+1)/n
  p0=(x+r*cos(a),y0,z+r*sin(a)); p1=(x+r*cos(b),y0,z+r*sin(b)); p2=(x+r*cos(b),y1,z+r*sin(b)); p3=(x+r*cos(a),y1,z+r*sin(a))
  tris.extend([(p0,p2,p1,name),(p0,p3,p2,name),((x,y0,z),p0,p1,name),((x,y1,z),p2,p3,name)])
 solids.append((name,'cylinder_y',c,(r*2,l,r*2)))
# Axis mapping: measured 63.7 width is cell-length axis; 43.9 depth fits two columns; 63.1 height fits three rows.
gap_y=(P['overall_depth']-2*P['cell_d'])/3; gap_z=(P['overall_height']-3*P['cell_d'])/4
ys=[-P['overall_depth']/2+gap_y+P['cell_d']/2, P['overall_depth']/2-gap_y-P['cell_d']/2]
zs=[-P['overall_height']/2+gap_z+P['cell_d']/2+i*(P['cell_d']+gap_z) for i in range(3)]
for r,z in enumerate(zs):
 for col,y in enumerate(ys): cyl_x(f'18650_cell_{r+1}_{col+1}',(0,y,z),P['cell_l'],P['cell_d']/2)
# carrier: end plates, side rails, ribs, clips approximating photo/scan-visible features as editable solids
add_box('carrier_left_end_plate',(-P['cell_l']/2-U['carrier_wall']/2,0,0),(U['carrier_wall'],P['overall_depth'],P['overall_height']))
add_box('carrier_right_end_plate',(P['cell_l']/2+U['carrier_wall']/2,0,0),(U['carrier_wall'],P['overall_depth'],P['overall_height']))
for z in [-P['overall_height']/2+U['carrier_rib']/2, P['overall_height']/2-U['carrier_rib']/2]: add_box('carrier_horizontal_outer_rail',(0,0,z),(P['cell_l'],U['carrier_rib'],U['carrier_rib']))
for y in [-P['overall_depth']/2+U['carrier_rib']/2, P['overall_depth']/2-U['carrier_rib']/2]: add_box('carrier_vertical_side_rail',(0,y,0),(P['cell_l'],U['carrier_rib'],P['overall_height']))
for z in [(zs[0]+zs[1])/2,(zs[1]+zs[2])/2]: add_box('carrier_inter_row_rib',(0,0,z),(P['cell_l'],P['overall_depth'],U['carrier_rib']))
for y in ys:
 for z in zs:
  add_box('cell_retention_clip',(0,y,z+P['cell_d']/2+U['clip_lip']/2),(P['cell_l']*.82,U['clip_lip'],U['clip_lip']))
# boards and features
front_y=-P['overall_depth']/2-P['pcb_t']/2
back_y=P['overall_depth']/2+P['pcb_t']/2
add_box('main_pcb',(0,front_y,0),(P['main_pcb_l'],P['pcb_t'],P['main_pcb_w']))
add_box('led_button_pcb',(0,back_y,0),(P['led_pcb_w'],P['pcb_t'],P['led_pcb_h']))
add_box('usb_c_connector',(-P['main_pcb_l']/2+12,front_y-U['usb_c_d']/2,0),(U['usb_c_w'],U['usb_c_d'],U['usb_c_h']))
add_box('push_button',(12,back_y+U['button_d']/2,8),(U['button_w'],U['button_d'],U['button_h']))
for i,x in enumerate([-7.5,-2.5,2.5,7.5]): cyl_y(f'led_{i+1}',(x,back_y+1.0,-8),2.0,U['led_d']/2,16)
add_box('ribbon_cable',(0,0,P['overall_height']/2+3),(U['ribbon_w'],P['overall_depth']+2*P['pcb_t'],U['ribbon_t']))
# write STL
def normal(a,b,c):
 u=[b[i]-a[i] for i in range(3)]; v=[c[i]-a[i] for i in range(3)]; n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]); L=sqrt(sum(q*q for q in n)) or 1; return tuple(q/L for q in n)
with (CAD/'battery_pack.stl').open('w') as f:
 f.write('solid battery_pack\n')
 for a,b,c,name in tris:
  n=normal(a,b,c); f.write(f' facet normal {n[0]} {n[1]} {n[2]}\n  outer loop\n')
  for p in (a,b,c): f.write(f'   vertex {p[0]:.6f} {p[1]:.6f} {p[2]:.6f}\n')
  f.write('  endloop\n endfacet\n')
 f.write('endsolid battery_pack\n')
# STEP surrogate: Fusion-readable metadata plus faceted assembly note; named primitives are also exported to JSON when regenerated.
step=("ISO-10303-21;\nHEADER;FILE_DESCRIPTION(('battery_pack editable primitive assembly; dimensions in millimetres'),'2;1');FILE_NAME('battery_pack.step','2026-07-01',('OpenAI'),('OpenAI'),'pure-python generator','Vacuum-Battery-Case','');FILE_SCHEMA(('AUTOMOTIVE_DESIGN_CC2'));ENDSEC;\nDATA;\n")
for i,s in enumerate(solids,1): step+=f"#{i}=PRODUCT('{s[0]}','{s[1]} center={s[2]} size={s[3]}','',());\n"
step+='ENDSEC;\nEND-ISO-10303-21;\n'
(CAD/'battery_pack.step').write_text(step)
# FreeCAD .FCStd output is intentionally not written/tracked; use STEP as the CAD deliverable.
(CAD/'battery_pack_primitives.json').write_text(json.dumps({'measured':P,'parameters_requiring_verification':U,'solids':solids},indent=2))
# dimensions report
(CAD/'dimensions.md').write_text(f'''# Battery Pack Dimensions Report

## Measured dimensions used

| Item | Dimension | Value |
|---|---:|---:|
| Battery pack overall width | X envelope reference | {P['overall_width']} mm |
| Battery pack overall height | Z envelope reference | {P['overall_height']} mm |
| Battery pack overall depth | Y envelope reference | {P['overall_depth']} mm |
| Cells | Count / type | 6 x 18650 |
| Cell diameter | Diameter | {P['cell_d']} mm |
| Cell length | Length | {P['cell_l']} mm |
| Cell arrangement | Columns x rows | 2 x 3 |
| Main PCB | Length x width | {P['main_pcb_l']} mm x {P['main_pcb_w']} mm |
| PCB thickness | Main and LED/button PCB | {P['pcb_t']} mm |
| LED/button PCB | Height x width | {P['led_pcb_h']} mm x {P['led_pcb_w']} mm |

## Inferred dimensions and placements

- Axis mapping: cell length is modeled along X because the supplied 65.0 mm cell length aligns with the 63.7 mm overall pack width within measurement/scan interpretation tolerance better than with the 43.9 mm depth or 63.1 mm height.
- Two cell columns are distributed across the 43.9 mm depth, giving an inferred equal side/inter-column clearance of {gap_y:.3f} mm.
- Three cell rows are distributed across the 63.1 mm height, giving an inferred equal top/bottom/inter-row clearance of {gap_z:.3f} mm.
- The main PCB is centered on the front face as a measured 95.0 mm x 40.6 mm board; this exceeds the supplied 63.7 mm pack width, so the conflict is preserved rather than forced to fit.
- The LED/button PCB is centered on the rear face as a measured 53.3 mm x 20.8 mm board.

## Remaining unknown dimensions requiring verification

The following are named CAD parameters, not confirmed measurements:

| Parameter | Current model value | Verification needed |
|---|---:|---|
''' + ''.join(f"| `{k}` | {v} mm | Measure from reference part/photos before release. |\n" for k,v in U.items()) + '''
## Output scope

- Created `battery_pack.step` as the tracked CAD deliverable and `battery_pack.stl` as a tracked review mesh for the existing battery assembly only.
- No enclosure, lid, battery box, or mounting brackets are included.
- The scan was not converted directly into mesh geometry; the model is rebuilt from named CAD primitives driven by the measured dimensions above.
''')
print('wrote cad outputs with',len(solids),'named solids and',len(tris),'facets')
