// Vacuum battery enclosure V1 - test fit only
// Reference: cad/step02_battery_assembly.step / .stl
// Coordinate convention: X=length, Y=width, Z=height. Split at mid-height.

part = "assembly"; // "bottom", "top", or "assembly"
$fn = 48;

battery = [96.7, 56.86, 55.2];
clearance = 0.8;              // target internal clearance per side
wall = 2.8;                   // FDM wall thickness target
floor = 2.8;
lid_thickness = 2.8;
lip = 1.8;
split_z = 31.0;               // lower internal depth; battery drops into lower half
screw_d = 3.2;                // M3 clearance
post_od = 7.5;
post_inset = 8;
usb_cutout = [16, wall + 0.8, 9];
button_cutout = [14, 14, lid_thickness + 1];
led_cutout = [28, 7, lid_thickness + 1];

inner = [battery[0] + 2*clearance, battery[1] + 2*clearance, battery[2] + 2*clearance];
outer = [inner[0] + 2*wall, inner[1] + 2*wall, inner[2] + floor + lid_thickness];

module screw_locations() {
  for (x=[-outer[0]/2+post_inset, outer[0]/2-post_inset])
    for (y=[-outer[1]/2+post_inset, outer[1]/2-post_inset])
      translate([x,y,0]) children();
}

module bottom() {
  difference() {
    union() {
      translate([-outer[0]/2,-outer[1]/2,0]) cube([outer[0], outer[1], split_z + floor]);
      screw_locations() translate([0,0,floor]) cylinder(d=post_od, h=split_z-1);
    }
    translate([-inner[0]/2,-inner[1]/2,floor]) cube([inner[0], inner[1], split_z + 2]);
    // USB-C access on front/negative Y wall
    translate([-usb_cutout[0]/2, -outer[1]/2-0.1, floor+12]) cube(usb_cutout);
    screw_locations() translate([0,0,-0.5]) cylinder(d=screw_d, h=split_z+floor+1);
  }
}

module top() {
  top_h = inner[2] - split_z + lid_thickness + lip;
  difference() {
    union() {
      // lid cap
      translate([-outer[0]/2,-outer[1]/2,split_z+floor]) cube([outer[0], outer[1], lid_thickness]);
      // shallow alignment lip that nests inside bottom opening
      translate([-inner[0]/2+0.35,-inner[1]/2+0.35,split_z+floor-lip])
        cube([inner[0]-0.7, inner[1]-0.7, lip]);
      screw_locations() translate([0,0,split_z+floor-lip]) cylinder(d=post_od, h=lid_thickness+lip);
    }
    // open underside so the battery upper features have clearance
    translate([-inner[0]/2+wall,-inner[1]/2+wall,split_z+floor-lip-0.1])
      cube([inner[0]-2*wall, inner[1]-2*wall, lip+0.2]);
    // power button opening, placed on top near +X end from reference model
    translate([24, -12, split_z+floor-0.1]) cube(button_cutout, center=true);
    // LED window opening next to button
    translate([24, 10, split_z+floor-0.1]) cube(led_cutout, center=true);
    screw_locations() translate([0,0,split_z+floor-lip-0.5]) cylinder(d=screw_d, h=lid_thickness+lip+1);
  }
}

if (part == "bottom") bottom();
else if (part == "top") top();
else {
  bottom();
  translate([0,0,0.4]) top();
}
