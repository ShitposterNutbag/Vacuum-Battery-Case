# Vacuum Battery Assembly Digital Twin

This repository models the existing battery assembly and a separate two-piece 3D-printable enclosure derived from the committed battery assembly CAD. It does not create a battery box, tray, or unrelated mounting brackets.

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


## Enclosure outputs

The enclosure is generated around the committed `cad/battery_pack.step` assembly without modifying that battery geometry. The enclosure uses 2.0 mm walls, 0.3 mm minimum clearance, four M3 screw bosses, USB-C/LED/button alignment features, PCB standoffs, battery locating ribs, and ventilation features near the PCB.

Generated enclosure files:

- `cad/enclosure_base.FCStd`
- `cad/enclosure_lid.FCStd`
- `cad/enclosure_base.step`
- `cad/enclosure_lid.step`
- `cad/enclosure_base.stl`
- `cad/enclosure_lid.stl`
- `cad/enclosure_dimensions.md`

Regenerate the enclosure with:

```bash
python tools/build_enclosure.py
```
