from math import sin, cos, pi, sqrt
from pathlib import Path
CAD=Path('cad'); CAD.mkdir(exist_ok=True)
P=dict(overall_l=96.7, block_w=63.7, block_h=63.1, depth=43.9, cell_d=18.3, cell_l=65.0, led_pcb_l=53.3, led_pcb_w=20.8, main_pcb_w=40.6, pcb_t=1.14)
U=dict(main_pcb_length=96.7, carrier_end_plate=0.65, carrier_side_wall=1.15, carrier_rib=2.0, dc_jack_diameter=8.0, dc_jack_depth=10.0, usb_c_width=8.94, usb_c_height=3.26, usb_c_depth=7.35, pushbutton_width=6.0, pushbutton_height=3.5, pushbutton_depth=2.5, led_diameter=3.0, ribbon_clearance_width=12.0, ribbon_clearance_height=2.0)
tris=[]; solids=[]
def add_box(name,c,s):
 x,y,z=c; sx,sy,sz=s; x0,x1=x-sx/2,x+sx/2; y0,y1=y-sy/2,y+sy/2; z0,z1=z-sz/2,z+sz/2
 v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
 faces=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
 tris.extend((v[a],v[b],v[c],name) for a,b,c in faces); solids.append((name,'box',c,s))
def cyl_x(name,c,l,r,n=64):
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
# cell block: X length, Y two-cell depth, Z three-cell height
gap_y=(P['depth']-2*P['cell_d'])/3; gap_z=(P['block_h']-3*P['cell_d'])/4
ys=[-P['depth']/2+gap_y+P['cell_d']/2, P['depth']/2-gap_y-P['cell_d']/2]
zs=[-P['block_h']/2+gap_z+P['cell_d']/2+i*(P['cell_d']+gap_z) for i in range(3)]
for zi,z in enumerate(zs,1):
 for yi,y in enumerate(ys,1): cyl_x(f'18650_cell_row{zi}_col{yi}',(0,y,z),P['cell_l'],P['cell_d']/2)
# holder within locked block envelope 63.7 x 43.9 x 63.1
add_box('plastic_holder_left_end',(-P['block_w']/2+U['carrier_end_plate']/2,0,0),(U['carrier_end_plate'],P['depth'],P['block_h']))
add_box('plastic_holder_right_end',(P['block_w']/2-U['carrier_end_plate']/2,0,0),(U['carrier_end_plate'],P['depth'],P['block_h']))
for y in [-P['depth']/2+U['carrier_side_wall']/2, P['depth']/2-U['carrier_side_wall']/2]: add_box('plastic_holder_side_rail',(0,y,0),(P['block_w'],U['carrier_side_wall'],P['block_h']))
for z in [-P['block_h']/2+U['carrier_rib']/2, P['block_h']/2-U['carrier_rib']/2, (zs[0]+zs[1])/2, (zs[1]+zs[2])/2]: add_box('plastic_holder_cross_rib',(0,0,z),(P['block_w'],P['depth'],U['carrier_rib']))
# PCBs/features constrained to overall max length 96.7 and depth 43.9 envelope
front_y=-P['depth']/2+P['pcb_t']/2
back_y=P['depth']/2-P['pcb_t']/2
add_box('main_pcb',(0,front_y,0),(U['main_pcb_length'],P['pcb_t'],P['main_pcb_w']))
add_box('small_led_button_pcb',(0,back_y,0),(P['led_pcb_l'],P['pcb_t'],P['led_pcb_w']))
add_box('usb_charging_connector',(-P['overall_l']/2+U['usb_c_depth']/2,front_y,0),(U['usb_c_depth'],P['pcb_t'],U['usb_c_height']))
cyl_x('dc_jack',(-P['overall_l']/2+U['dc_jack_depth']/2,-P['depth']/2+U['dc_jack_diameter']/2,12),U['dc_jack_depth'],U['dc_jack_diameter']/2,32)
add_box('pushbutton',(8,P['depth']/2-U['pushbutton_depth']/2,6),(U['pushbutton_width'],U['pushbutton_depth'],U['pushbutton_height']))
for x in [-12,-4,4,12]: cyl_y('led_indicator',(x,back_y, -6),P['pcb_t'],U['led_diameter']/2,16)
add_box('ribbon_connector_clearance',(26,0,P['block_h']/2-U['ribbon_clearance_height']/2),(U['ribbon_clearance_width'],P['depth'],U['ribbon_clearance_height']))
def normal(a,b,c):
 u=[b[i]-a[i] for i in range(3)]; v=[c[i]-a[i] for i in range(3)]; n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]); L=sqrt(sum(q*q for q in n)) or 1; return tuple(q/L for q in n)
with (CAD/'battery_pack_v2.stl').open('w') as f:
 f.write('solid battery_pack_v2\n')
 for a,b,c,name in tris:
  n=normal(a,b,c); f.write(f' facet normal {n[0]:.6g} {n[1]:.6g} {n[2]:.6g}\n  outer loop\n')
  for p in (a,b,c): f.write(f'   vertex {p[0]:.6f} {p[1]:.6f} {p[2]:.6f}\n')
  f.write('  endloop\n endfacet\n')
 f.write('endsolid battery_pack_v2\n')
step="ISO-10303-21;\nHEADER;FILE_DESCRIPTION(('battery_pack_v2 corrected primitive assembly; dimensions in millimetres'),'2;1');FILE_NAME('battery_pack_v2.step','2026-07-01',('OpenAI'),('OpenAI'),'pure-python generator','Vacuum-Battery-Case','');FILE_SCHEMA(('AUTOMOTIVE_DESIGN_CC2'));ENDSEC;\nDATA;\n"
for i,s in enumerate(solids,1): step+=f"#{i}=PRODUCT('{s[0]}','{s[1]} center={s[2]} size={s[3]}','',());\n"
step+='ENDSEC;\nEND-ISO-10303-21;\n'
(CAD/'battery_pack_v2.step').write_text(step)
# bbox
pts=[p for tri in tris for p in tri[:3]]; mins=[min(p[i] for p in pts) for i in range(3)]; maxs=[max(p[i] for p in pts) for i in range(3)]
print('bbox', mins, maxs, [maxs[i]-mins[i] for i in range(3)], 'solids', len(solids))
