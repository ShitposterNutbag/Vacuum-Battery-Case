// Vacuum battery enclosure V2 bottom revision
// Based on the V1 fit envelope; this file focuses only on the bottom enclosure.
// Coordinate convention: X=length, Y=width, Z=height.

part = "bottom"; // "bottom" or "preview"
$fn = 48;

battery = [96.7, 56.86, 55.2];
clearance = 0.8;
wall = 2.8;
floor = 2.0;
bottom_height = 31.0 + floor;

rail_width = 3.0;
rail_inset_from_side_wall = 12.0;
rail_height_from_inside_bottom = 9.5;

dc_jack_opening = [wall + 0.8, 9.5, 7.5]; // X depth through short wall, Y width, Z height
show_debug_cutouts = (part == "preview");

inner = [battery[0] + 2*clearance, battery[1] + 2*clearance, battery[2] + 2*clearance];
outer = [inner[0] + 2*wall, inner[1] + 2*wall, inner[2] + floor + 2.8];
case_length = outer[0];
case_width = outer[1];

module dc_jack_cutout() {
  // On the -X short wall, centered horizontally across that short side (Y axis).
  // Bottom starts at the inside floor height, so Z = floor through floor + 7.5 mm.
  translate([-case_length/2 - 0.1, -dc_jack_opening[1]/2, floor])
    cube(dc_jack_opening);
}

module bottom_shell() {
  difference() {
    translate([-case_length/2, -case_width/2, 0])
      cube([case_length, case_width, bottom_height]);

    translate([-inner[0]/2, -inner[1]/2, floor])
      cube([inner[0], inner[1], bottom_height + 1]);

    dc_jack_cutout();
  }
}

module rail(y_sign) {
  y = y_sign * (inner[1]/2 - rail_inset_from_side_wall);
  translate([-inner[0]/2, y - rail_width/2, floor])
    cube([inner[0], rail_width, rail_height_from_inside_bottom]);
}

module bottom_case_v2() {
  color("yellow") bottom_shell();
  color("green") {
    rail(1);
    rail(-1);
  }
}

module debug_markers() {
  color("red", 0.55) dc_jack_cutout();
}

if (part == "bottom") {
  bottom_case_v2();
} else if (part == "preview") {
  bottom_case_v2();
  if (show_debug_cutouts) debug_markers();
}
