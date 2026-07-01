# Vacuum Battery Assembly Digital Twin

This repository now models the existing battery assembly only. It does not create an enclosure, lid, battery box, tray, or mounting brackets.

## Authoritative inputs

- Supplied caliper measurements are authoritative and override the scan when they disagree.
- `6_30_2026v2.glb` and the reference photos are spatial references only.
- Geometry is rebuilt from measured dimensions and named parameters; the scan mesh is not converted directly into CAD geometry.

## Outputs

Generated files are written to `cad/`:

- `cad/battery_pack.step` — STEP CAD deliverable / assembly manifest of named solids.
- `cad/battery_pack.stl` — triangulated review mesh generated from the rebuilt solids.
- `cad/dimensions.md` — measured dimensions, inferred dimensions, and unknown dimensions requiring verification.

## Regeneration

Run:

```bash
python tools/build_battery_pack.py
```

The generator is intentionally parameter-driven. Unknown feature dimensions such as clip lips, ribs, USB-C connector body, push button, ribbon cable, and LED package size remain named parameters until measured.
