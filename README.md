# Vacuum Battery Fit-Check Enclosure

This repository contains the committed visual reference assets `6_30_2026.glb`
and `drive-download-20260701T020457Z-3-001.zip`, plus an editable CadQuery model
and generated STL for the v2 open-top fit-check tray.

## V2 dimensions

The v2 model does **not** use the full GLB scan bounding box for final sizing,
because the scan includes surrounding artifacts. It uses the supplied real
measurements instead:

- Battery assembly: 97.6 mm × 66.2 mm × 61.5 mm
- Internal cavity: 99.0 mm × 67.5 mm × 63.0 mm
- Wall thickness: 2.5 mm
- Floor thickness: 2.5 mm
- Outside dimensions: 104.0 mm × 72.5 mm × 67.5 mm

## Outputs

- `vacuum_battery_case_v2.py` — editable CadQuery source for the open-top tray.
- `output/vacuum_battery_fit_check_v2.stl` — single printable STL output.
- `tools/generate_fit_check_stl.py` — dependency-free STL generator used in this
  environment when CadQuery is unavailable.

## Features

- DC barrel jack opening on the side wall: 13 mm × 10 mm, centered at X = 52.0
  mm and Z = 10.5 mm.
- Power button opening on the same side wall: 9 mm × 7 mm, centered at X = 41.0
  mm and Z = 23.0 mm.
- Four LED windows on the opposite wall near the open top.
- Four internal charging-PCB support posts raised above the floor for DC jack
  protrusion clearance.
