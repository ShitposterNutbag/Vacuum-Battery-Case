// Vacuum battery enclosure V2 - rail-retained tray, no posts
// Coordinate convention: X=length, Y=width, Z=height.
// The DC jack opening is placed on a short side wall: the -X wall.

part = "case";
$fn = 48;

battery = [96.7, 56.86, 55.2];
clearance = 0.8;
wall = 2.8;
floor = 2.8;

inner = [battery[0] + 2 * clearance, battery[1] + 2 * clearance, battery[2] + 2 * clearance];
outer = [inner[0] + 2 * wall, inner[1] + 2 * wall, inner[2] + floor];

// DC jack opening requirements: 9.5 mm wide x 7.5 mm high,
// with the bottom of the opening 2 mm above the outside bottom.
dc_jack_opening = [wall + 0.4, 9.5, 7.5];
dc_jack_bottom_from_outside = 2;
dc_jack_z = dc_jack_bottom_from_outside;

// Rail requirements: exactly two rails, 9.5 mm tall, inset 12 mm from each side,
// running the usable internal length of the case.
rail_count = 2;
rail_height = 9.5;
rail_side_inset = 12;
rail_width = 3.0;
rail_length = inner[0];
rail_y_positions = [
  -inner[1] / 2 + rail_side_inset,
   inner[1] / 2 - rail_side_inset - rail_width
];

module rails() {
  for (i = [0 : rail_count - 1]) {
    translate([-inner[0] / 2, rail_y_positions[i], floor])
      cube([rail_length, rail_width, rail_height]);
  }
}

module hollow_shell() {
  difference() {
    translate([-outer[0] / 2, -outer[1] / 2, 0])
      cube(outer);

    translate([-inner[0] / 2, -inner[1] / 2, floor])
      cube([inner[0], inner[1], inner[2] + 0.2]);

    // DC jack opening centered horizontally on the short -X side wall.
    translate([-outer[0] / 2 - 0.1, -dc_jack_opening[1] / 2, dc_jack_z])
      cube(dc_jack_opening);
  }
}

module case_body() {
  union() {
    hollow_shell();
    rails();
  }
}

if (part == "case") {
  case_body();
}
