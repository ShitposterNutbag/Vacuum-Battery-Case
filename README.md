# Vacuum Battery Open-Top Fit-Check Tray

This repository contains the cleaned scan `6_30_2026v2.glb`, caliper reference
photos, and a generated **open-top fit-check tray** STL for test fitting only.
The earlier `6_30_2026.glb` scan is retained in the repository but is not used
for the current tray.

## Current reference assumptions

- `6_30_2026v2.glb` is the authoritative cleaned scan.
- The scan is scaled at `50.0 mm` per scan unit, matching the caliper-photo
  scale check used for this fit-check pass.
- The battery stands upright.
- The scan X axis is treated as battery width, scan Z as upright height, and
  scan Y as PCB-to-PCB depth.
- The long PCB is the primary face and contains the DC barrel jack plus main
  power button.
- The short PCB is on the opposite side and contains LEDs plus the original
  vacuum high/low button; the short-board button should not receive a functional
  external opening.

## Output

- `output/vacuum_battery_fit_check_tray.stl` — open-top test-fit tray only.
- `tools/generate_fit_check_stl.py` — dependency-free generator used to create
  the tray STL from `6_30_2026v2.glb`.

The generated tray is intentionally not the final enclosure. It includes a floor,
side retention walls, corner posts, and coarse reliefs on the long-PCB primary
face for test fitting around the DC barrel jack and main power button area. It
intentionally does not add a functional opening for the short-PCB vacuum mode
button.
