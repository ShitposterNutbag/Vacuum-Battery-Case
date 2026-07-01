# Vacuum Battery Assembly CAD Review Model

This repository is currently focused on modeling **only the battery assembly**
for review. Tray and enclosure generation are intentionally stopped until the
battery model is approved.

## Authoritative references

- `6_30_2026v2.glb` is the cleaned scan used for the current assembly model.
- The caliper photos and uploaded measurements are the scaling references for
  this review pass.
- The earlier `6_30_2026.glb` scan is retained but is not used for the current
  model.

## Current assembly-model assumptions

- The battery stands upright.
- The scan X axis is battery width, scan Z is upright height, and scan Y is the
  PCB-to-PCB depth.
- The model uses `50.0 mm` per scan unit, yielding a cleaned-scan envelope of
  approximately `114.9 mm W x 16.7 mm D x 125.9 mm H`.
- The long PCB is the primary face and includes the DC barrel jack, main power
  button, and board connector.
- The short PCB is on the opposite side and includes LEDs, the original vacuum
  mode button, and a board connector. The vacuum mode button is modeled for
  review only and is not marked as an external-opening target.

## Output

- `output/vacuum_battery_assembly_model.stl` — battery-assembly review model
  only.
- `output/vacuum_battery_assembly_model.json` — scale, source-scan, and modeled
  component manifest for review.
- `tools/generate_battery_assembly_model.py` — dependency-free generator for the
  assembly review STL and manifest.

## Scope boundaries

This model includes the six-cell pack, battery holders/rails, both PCB boards,
DC jack, main power button, LEDs, vacuum mode button, wiring, and connectors.
It does **not** generate a fit-check tray, enclosure, shell, or rectangular-prism
placeholder. A tray should only be generated after this assembly model is
reviewed and approved.
