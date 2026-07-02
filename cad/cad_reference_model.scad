// Simplified CAD reference from cleaned RealityScan mesh.
// Units: millimetres. This is a dimensional/keep-out reference only,
// not an enclosure and not production geometry.

$fn = 48;

// Cleaned mesh bounding box measured by scripts/clean_realityscan_mesh.py output.
mesh_min = [-160.609, 60.176, -266.145];
mesh_max = [124.599, 333.437, 176.042];
overall = [285.208, 273.261, 442.187];

// Origin normalized to cleaned mesh minimum corner for easier enclosure planning.
module overall_scan_envelope() {
  color([0.8, 0.8, 0.8, 0.18])
    translate([0, 0, 0]) cube(overall, center=false);
}

module cell_block() {
  // Six-cell block represented as tangent 18650 cells, scaled up to occupy the
  // major cell mass seen in the cleaned mesh. Verify exact cell pitch manually.
  cell_d = 18.4;
  cell_l = 65.2;
  pitch = cell_d;
  scale_to_scan = min(overall[0] * 0.78 / (3 * pitch), overall[2] * 0.70 / cell_l);
  sx = scale_to_scan;

  translate([overall[0] * 0.11, overall[1] * 0.18, overall[2] * 0.13])
    scale([sx, sx, sx])
      for (row = [0:1], col = [0:2])
        translate([col * pitch, row * pitch, 0])
          rotate([0, 90, 0])
            color([0.15, 0.15, 0.15, 0.55]) cylinder(d=cell_d, h=cell_l, center=false);
}

module pcb() {
  // Main PCB/reference plane. Captures electronics keep-out rather than component detail.
  color([0.0, 0.45, 0.12, 0.65])
    translate([overall[0] * 0.19, overall[1] * 0.70, overall[2] * 0.30])
      cube([overall[0] * 0.62, overall[1] * 0.035, overall[2] * 0.36], center=false);
}

module usb_c_charging_board() {
  color([0.05, 0.2, 0.75, 0.8])
    translate([overall[0] * 0.38, overall[1] * 0.75, overall[2] * 0.42])
      cube([overall[0] * 0.24, overall[1] * 0.055, overall[2] * 0.11], center=false);

  // USB-C port/opening marker on the outward face of the small board.
  color([0.02, 0.02, 0.02, 1.0])
    translate([overall[0] * 0.45, overall[1] * 0.807, overall[2] * 0.455])
      cube([overall[0] * 0.10, overall[1] * 0.018, overall[2] * 0.032], center=false);
}

module power_button() {
  color([0.9, 0.1, 0.1, 0.85])
    translate([overall[0] * 0.50, overall[1] * 0.825, overall[2] * 0.62])
      rotate([90, 0, 0]) cylinder(d=overall[0] * 0.075, h=overall[1] * 0.035, center=true);
}

module leds() {
  for (i = [0:3])
    color([1.0, 0.86, 0.1, 0.9])
      translate([overall[0] * (0.37 + i * 0.085), overall[1] * 0.828, overall[2] * 0.57])
        rotate([90, 0, 0]) cylinder(d=overall[0] * 0.030, h=overall[1] * 0.025, center=true);
}

module cad_reference_model() {
  overall_scan_envelope();
  cell_block();
  pcb();
  usb_c_charging_board();
  power_button();
  leds();
}

cad_reference_model();
