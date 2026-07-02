// Vacuum battery enclosure V2 - enclosure-only revision
// Reference: cad/step02_battery_assembly.step / .stl
// Coordinate convention: X=length, Y=width, Z=height. Split at mid-height.
// V2 preserves the V1 outer envelope and battery cavity, while replacing
// first-pass placeholder openings with oversized rectangular functional cuts.

part = "assembly"; // "bottom", "top", or "assembly"
$fn = 48;

battery = [96.7, 56.86, 55.2];
clearance = 0.8;              // target internal clearance per side
wall = 2.8;                   // FDM wall thickness target
floor = 2.8;
lid_thickness = 2.8;
lip = 1.8;
split_z = 31.0;               // lower internal depth; battery drops into lower half
screw_d = 3.2;                // M3 clearance; screw holes remain cylindrical by intent
post_od = 7.5;
post_inset = 8;

// V2 functional openings. These are intentionally oversized where the scan
// does not provide a reliable exact board location; refine after test print.
usb_board_cutout = [24, wall + 1.2, 14];   // rectangular charging-board/USB access
usb_board_pos = [0, 0, floor + 13.5];      // centered on front/negative-Y wall
button_cutout = [16, 16, lid_thickness + 1.2];
button_pos = [24, -12, 0];
led_hole_d = 3.4;
led_pitch = 6.0;
led_count = 4;
led_window_cutout = [led_pitch*(led_count-1) + led_hole_d + 3, 7, lid_thickness + 1.2];
led_pos = [24, 10, 0];

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
    // Preserve V1 battery cavity and 0.8 mm per-side clearance.
    translate([-inner[0]/2,-inner[1]/2,floor]) cube([inner[0], inner[1], split_z + 2]);
    // Oversized rectangular access for charging board and USB connector.
    translate([usb_board_pos[0]-usb_board_cutout[0]/2, -outer[1]/2-0.1, usb_board_pos[2]-usb_board_cutout[2]/2])
      cube(usb_board_cutout);
    screw_locations() translate([0,0,-0.5]) cylinder(d=screw_d, h=split_z+floor+1);
  }
}

module top() {
  top_h = inner[2] - split_z + lid_thickness + lip;
  difference() {
    union() {
      // lid cap; V2 preserves V1 outer dimensions.
      translate([-outer[0]/2,-outer[1]/2,split_z+floor]) cube([outer[0], outer[1], lid_thickness]);
      // shallow alignment lip that nests inside bottom opening
      translate([-inner[0]/2+0.35,-inner[1]/2+0.35,split_z+floor-lip])
        cube([inner[0]-0.7, inner[1]-0.7, lip]);
      screw_locations() translate([0,0,split_z+floor-lip]) cylinder(d=post_od, h=lid_thickness+lip);
    }
    // open underside so the battery upper features have clearance
    translate([-inner[0]/2+wall,-inner[1]/2+wall,split_z+floor-lip-0.1])
      cube([inner[0]-2*wall, inner[1]-2*wall, lip+0.2]);
    // Oversized rectangular power-button access.
    translate([button_pos[0], button_pos[1], split_z+floor-0.1]) cube(button_cutout, center=true);
    // Rectangular LED visibility slot; individual LED centers are documented below for refinement.
    translate([led_pos[0], led_pos[1], split_z+floor-0.1]) cube(led_window_cutout, center=true);
    screw_locations() translate([0,0,split_z+floor-lip-0.5]) cylinder(d=screw_d, h=lid_thickness+lip+1);
  }
}

if (part == "bottom") bottom();
else if (part == "top") top();
else {
  bottom();
  translate([0,0,0.4]) top();
}
