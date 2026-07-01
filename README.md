# Vacuum Battery Fit-Check Enclosure

This repository contains the committed scan `6_30_2026.glb`, the committed
reference photo archive `drive-download-20260701T020457Z-3-001.zip`, editable
CadQuery source, and a generated printable STL fit-check enclosure.

## Outputs

- `cad/vacuum_battery_case.py` — editable CadQuery source. It reads the GLB scan
  bounding box and exposes parameters for clearance, wall thickness, USB-C,
  charging-module, switch, and LED features.
- `output/vacuum_battery_fit_check_enclosure.stl` — printable fit-check STL.
- `tools/generate_fit_check_stl.py` — dependency-free STL generator used in this
  environment when CadQuery is unavailable.

The STL is intended as a first fit-check print around the scan envelope. The LED
features are shallow drill guides so their final diameters can be tuned after the
first print.
