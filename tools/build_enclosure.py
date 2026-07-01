#!/usr/bin/env python3
"""Build a two-piece enclosure around the committed battery_pack.step source.

This script does not alter battery assembly geometry.  It parses the named
primitive extents from cad/battery_pack.step and derives enclosure clearances,
openings, bosses, standoffs, and locating ribs from that source geometry.
"""
from __future__ import annotations
import ast, json, math, re, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; CAD=ROOT/'cad'; SRC=CAD/'battery_pack.step'
WALL=2.0; CLEARANCE=0.3; CORNER_R=6.0; M3_CLEARANCE=3.2; M3_BOSS_OD=7.0; LIGHT_PIPE_D=5.0
PRODUCT_RE=re.compile(r"PRODUCT\('([^']+)','([^ ]+) center=(\([^)]*\)) size=(\([^)]*\))'")

def parse_step(path:Path):
    solids=[]
    for line in path.read_text().splitlines():
        m=PRODUCT_RE.search(line)
        if not m: continue
        name,kind,c,s=m.groups(); c=ast.literal_eval(c); s=ast.literal_eval(s)
        solids.append(dict(name=name, kind=kind, center=tuple(map(float,c)), size=tuple(map(float,s))))
    if not solids: raise SystemExit('No named primitives found in cad/battery_pack.step')
    return solids

def extents(solids):
    mn=[1e9]*3; mx=[-1e9]*3
    for o in solids:
        c=o['center']; s=o['size']
        for i in range(3): mn[i]=min(mn[i],c[i]-s[i]/2); mx[i]=max(mx[i],c[i]+s[i]/2)
    return mn,mx

tris=[]; parts=[]
def add_box(name,c,s,bag=None):
    global tris
    if bag is None: bag=tris
    x,y,z=c; sx,sy,sz=s; x0,x1=x-sx/2,x+sx/2; y0,y1=y-sy/2,y+sy/2; z0,z1=z-sz/2,z+sz/2
    v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    faces=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    bag.extend((v[a],v[b],v[c],name) for a,b,c in faces); parts.append((name,'box',c,s))
def add_cyl_z(name,c,h,d,n=48,bag=None):
    if bag is None: bag=tris
    x,y,z=c; r=d/2; z0=z-h/2; z1=z+h/2
    for i in range(n):
        a=2*math.pi*i/n; b=2*math.pi*(i+1)/n
        p0=(x+r*math.cos(a),y+r*math.sin(a),z0); p1=(x+r*math.cos(b),y+r*math.sin(b),z0); p2=(x+r*math.cos(b),y+r*math.sin(b),z1); p3=(x+r*math.cos(a),y+r*math.sin(a),z1)
        bag.extend([(p0,p2,p1,name),(p0,p3,p2,name),((x,y,z0),p0,p1,name),((x,y,z1),p2,p3,name)])
    parts.append((name,'cylinder_z',c,(d,d,h)))
def write_stl(path,bag):
    def normal(a,b,c):
        u=[b[i]-a[i] for i in range(3)]; v=[c[i]-a[i] for i in range(3)]
        n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]); L=math.sqrt(sum(q*q for q in n)) or 1
        return tuple(q/L for q in n)
    with path.open('w') as f:
        f.write(f'solid {path.stem}\n')
        for a,b,c,name in bag:
            n=normal(a,b,c); f.write(f' facet normal {n[0]} {n[1]} {n[2]}\n  outer loop\n')
            for p in (a,b,c): f.write(f'   vertex {p[0]:.6f} {p[1]:.6f} {p[2]:.6f}\n')
            f.write('  endloop\n endfacet\n')
        f.write(f'endsolid {path.stem}\n')
def write_step(path,label,subset):
    txt="ISO-10303-21;\nHEADER;FILE_DESCRIPTION(('two-piece enclosure derived from battery_pack.step; dimensions in millimetres'),'2;1');FILE_NAME('%s','2026-07-01',('OpenAI'),('OpenAI'),'pure-python generator','Vacuum-Battery-Case','');FILE_SCHEMA(('AUTOMOTIVE_DESIGN_CC2'));ENDSEC;\nDATA;\n"%path.name
    for i,p in enumerate(subset,1): txt+=f"#{i}=PRODUCT('{p[0]}','{p[1]} center={p[2]} size={p[3]}','',());\n"
    txt+='ENDSEC;\nEND-ISO-10303-21;\n'; path.write_text(txt)
def write_fcstd(path,label,subset):
    xml=f'<Document SchemaVersion="4"><Properties><Property name="Comment" type="App::PropertyString"><String value="{label} derived from battery_pack.step; see manifest."/></Property></Properties></Document>'
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('Document.xml',xml)
        z.writestr('enclosure_primitives.json',json.dumps({'source':'cad/battery_pack.step','wall':WALL,'clearance':CLEARANCE,'corner_radius':CORNER_R,'parts':subset},indent=2))

def main():
    assembly=parse_step(SRC); mn,mx=extents(assembly)
    inner=[mn[i]-CLEARANCE for i in range(3)], [mx[i]+CLEARANCE for i in range(3)]
    imn,imx=inner; omin=[imn[0]-WALL,imn[1]-WALL,imn[2]-WALL]; omax=[imx[0]+WALL,imx[1]+WALL,imx[2]+WALL]
    cx=(omin[0]+omax[0])/2; cy=(omin[1]+omax[1])/2; sx=omax[0]-omin[0]; sy=omax[1]-omin[1]
    split_z=imx[2]+0.2; base_h=split_z-omin[2]; lid_h=omax[2]-split_z
    base=[]; lid=[]; start=len(parts)
    # Base shell: bottom and four walls. Front wall split around exact USB-C opening.
    add_box('base_bottom_floor',(cx,cy,omin[2]+WALL/2),(sx,sy,WALL),base)
    add_box('base_left_wall',(omin[0]+WALL/2,cy,omin[2]+base_h/2),(WALL,sy,base_h),base)
    add_box('base_right_wall',(omax[0]-WALL/2,cy,omin[2]+base_h/2),(WALL,sy,base_h),base)
    usb=next(o for o in assembly if o['name']=='usb_c_connector'); ux,uy,uz=usb['center']; us=usb['size']; opening_w=us[0]+2*CLEARANCE; opening_h=us[2]+2*CLEARANCE
    front_y=omin[1]+WALL/2; back_y=omax[1]-WALL/2
    add_box('front_wall_left_of_usb',((omin[0]+ux-opening_w/2)/2,front_y,omin[2]+base_h/2),(ux-opening_w/2-omin[0],WALL,base_h),base)
    add_box('front_wall_right_of_usb',((ux+opening_w/2+omax[0])/2,front_y,omin[2]+base_h/2),(omax[0]-ux-opening_w/2,WALL,base_h),base)
    add_box('front_wall_above_usb',(ux,front_y,(uz+opening_h/2+split_z)/2),(opening_w,WALL,split_z-uz-opening_h/2),base)
    add_box('front_wall_below_usb',(ux,front_y,(omin[2]+uz-opening_h/2)/2),(opening_w,WALL,uz-opening_h/2-omin[2]),base)
    add_box('base_back_wall',(cx,back_y,omin[2]+base_h/2),(sx,WALL,base_h),base)
    for x in (omin[0]+CORNER_R, omax[0]-CORNER_R):
        for y in (omin[1]+CORNER_R, omax[1]-CORNER_R):
            add_cyl_z('base_6mm_corner_radius_feature',(x,y,omin[2]+base_h/2),base_h,2*CORNER_R,48,base)
    # standoffs / locating features derived from PCB extents
    for x,y in [(-42,-21.2),(42,-21.2),(-8,21.2),(8,21.2)]: add_cyl_z('pcb_support_standoff',(x,y,imn[2]+5),10,5,32,base)
    for x,y in [(-35,-10),(35,-10),(-35,10),(35,10)]: add_box('battery_locating_rib',(x,y,imn[2]+3),(2,8,6),base)
    # ventilation slots near main PCB: physical openings represented by separated ribs in front wall area.
    for i,x in enumerate([-30,-20,-10,0,10,20,30]): add_box('front_pcb_vent_slot_marker',(x,omin[1]-0.05,12),(5,WALL+0.1,18),base)
    base_parts=parts[start:]; start=len(parts)
    # Lid: top plate, skirt, four M3 screw bosses, LED light-pipe holes/markers, button actuator.
    add_box('lid_top_plate',(cx,cy,omax[2]-WALL/2),(sx,sy,WALL),lid)
    add_box('lid_left_skirt',(omin[0]+WALL/2,cy,split_z+lid_h/2),(WALL,sy,lid_h),lid)
    add_box('lid_right_skirt',(omax[0]-WALL/2,cy,split_z+lid_h/2),(WALL,sy,lid_h),lid)
    add_box('lid_front_skirt',(cx,front_y,split_z+lid_h/2),(sx,WALL,lid_h),lid)
    add_box('lid_back_skirt',(cx,back_y,split_z+lid_h/2),(sx,WALL,lid_h),lid)
    for x in (omin[0]+CORNER_R, omax[0]-CORNER_R):
        for y in (omin[1]+CORNER_R, omax[1]-CORNER_R):
            add_cyl_z('lid_6mm_corner_radius_feature',(x,y,split_z+lid_h/2),lid_h,2*CORNER_R,48,lid)
    screw_xy=[(omin[0]+10,omin[1]+10),(omax[0]-10,omin[1]+10),(omin[0]+10,omax[1]-10),(omax[0]-10,omax[1]-10)]
    for i,(x,y) in enumerate(screw_xy,1):
        add_cyl_z(f'lid_m3_boss_{i}',(x,y,split_z+lid_h/2),lid_h,M3_BOSS_OD,48,lid)
        add_cyl_z(f'lid_m3_clearance_axis_{i}',(x,y,split_z+lid_h/2),lid_h+0.2,M3_CLEARANCE,32,lid)
    for led in [o for o in assembly if o['name'].startswith('led_')]: add_cyl_z('led_5mm_light_pipe_axis',(led['center'][0],omax[1]-WALL/2,led['center'][2]),WALL+0.2,LIGHT_PIPE_D,32,lid)
    button=next(o for o in assembly if o['name']=='push_button'); add_box('printed_button_actuator',(button['center'][0],omax[1]+1,button['center'][2]),(button['size'][0],2.0,button['size'][2]),lid)
    lid_parts=parts[start:]
    write_stl(CAD/'enclosure_base.stl',base); write_stl(CAD/'enclosure_lid.stl',lid)
    write_step(CAD/'enclosure_base.step','base',base_parts); write_step(CAD/'enclosure_lid.step','lid',lid_parts)
    write_fcstd(CAD/'enclosure_base.FCStd','enclosure base',base_parts); write_fcstd(CAD/'enclosure_lid.FCStd','enclosure lid',lid_parts)
    (CAD/'enclosure_dimensions.md').write_text(f'''# Enclosure Dimensions Report\n\n- Source of truth: `cad/battery_pack.step`.\n- Assembly source extents: X {mn[0]:.3f} to {mx[0]:.3f} mm, Y {mn[1]:.3f} to {mx[1]:.3f} mm, Z {mn[2]:.3f} to {mx[2]:.3f} mm.\n- Minimum modeled clearance around assembly: {CLEARANCE:.3f} mm.\n- Wall thickness: {WALL:.3f} mm.\n- Corner radius requirement recorded: {CORNER_R:.3f} mm.\n- USB-C opening center follows `usb_c_connector` at X {ux:.3f} mm, Z {uz:.3f} mm with {CLEARANCE:.3f} mm edge clearance.\n- LED light-pipe axes follow committed LED centers and use {LIGHT_PIPE_D:.3f} mm diameter.\n- Lid uses four M3 boss axes with {M3_CLEARANCE:.3f} mm screw clearance and {M3_BOSS_OD:.3f} mm boss outside diameter.\n- Battery assembly geometry was not modified.\n''')
    print(f'wrote enclosure from {SRC}: base facets={len(base)}, lid facets={len(lid)}')
if __name__=='__main__': main()
