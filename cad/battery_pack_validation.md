# Battery Pack CAD Validation Report

## Scope and authority

This validation stops enclosure work and reviews only the master battery assembly CAD. The authoritative dimensional inputs are the committed caliper/photo-derived values listed by the user, with the committed Polycam GLB files used only as visual/spatial orientation references. The existing `cad/battery_pack.step` is not assumed to be correct.

Reference files checked:

- `6_30_2026.glb`
- `6_30_2026v2.glb`
- `cad/battery_pack.step`
- `cad/battery_pack.stl`
- committed measurement/photo assets including `IMG_9487.HEIC`, `IMG_9488.HEIC`, `IMG_9490.HEIC`, and `drive-download-20260701T020457Z-3-001.zip`

## GLB scan comparison

Both Polycam GLB files contain the same single mesh bounds in their embedded glTF accessor metadata:

| File | Raw accessor min | Raw accessor max | Raw raw-units extents |
|---|---:|---:|---:|
| `6_30_2026.glb` | `[-1.14935, ~0, -1.25908]` | `[1.14935, 0.33344, 1.25908]` | `[2.29870, 0.33344, 2.51817]` |
| `6_30_2026v2.glb` | `[-1.14935, ~0, -1.25908]` | `[1.14935, 0.33344, 1.25908]` | `[2.29870, 0.33344, 2.51817]` |

The GLBs do not provide millimetre-authenticated dimensions by themselves. They are useful for part layout and orientation, but scale must come from the caliper measurements/photos.

## Existing `cad/battery_pack.step` origin

`cad/battery_pack.step` was recreated parametrically, not converted directly from the cleaned Polycam scan. The STEP file is a lightweight STEP surrogate containing named primitive `PRODUCT` records such as six `cylinder_x` 18650 cells, carrier boxes, PCB boxes, USB/button/LED primitives, and metadata that explicitly identifies it as an editable primitive assembly. The companion generator and existing dimensions report also state that the scan was not converted directly into mesh geometry.

Answer: **parametrically recreated**, not directly based on the cleaned Polycam mesh.

## Existing orientation check

The existing assembly orients the six cells along the STEP/STL X axis, arranges two cells across Y, and stacks three rows along Z. That orientation is consistent with the intended cleaned-scan layout: long pack direction on X, full pack/cell depth on Y, and three-cell stack height on Z.

Answer: **orientation generally matches the cleaned GLB scan/reference layout**, but the dimensional envelope is not validated by orientation alone.

## Existing dimensional check against locked measurements

Parsed existing `cad/battery_pack.stl` extents:

| Axis | Existing extent | Locked/reference requirement | Result |
|---|---:|---:|---|
| X / overall assembly length | 95.0 mm | 96.7 mm max assembly length | **Mismatch**: short by 1.7 mm |
| Y / full pack depth | 54.89 mm | 43.9 mm full pack depth/cell depth reference | **Mismatch**: too deep by 10.99 mm |
| Z / block height | 66.275 mm | 63.1 mm battery/cell block height | **Mismatch**: too tall by 3.175 mm |

Individual locked checks:

| Locked item | Existing model status | Result |
|---|---|---|
| Six 18650 cells | Six `cylinder_x` cell primitives are present | Pass |
| 2 rows x 3 cells | Existing model has two columns across depth and three rows in height | Pass |
| Overall max assembly length: 96.7 mm | Existing STL/STEP envelope is 95.0 mm because `main_pcb` is modelled as 95.0 mm long | Fail |
| Battery/cell block width: 63.7 mm | Existing carrier is effectively 66.6 mm across the cell-length axis because it uses 65.0 mm cells plus 1.6 mm end plates outside the cells | Fail |
| Battery/cell block height: 63.1 mm | Existing carrier uses 63.1 mm, but clips/ribbon push total STL height to 66.275 mm | Fail for total block envelope control |
| Cell diameter: 18.3 mm | Existing cells use 18.3 mm diameter | Pass |
| Cell length: 65.0 mm | Existing cells use 65.0 mm length | Pass |
| Small LED/button PCB length: 53.3 mm | Existing model assigns 53.3 mm to the Z dimension of the LED/button PCB, not its long in-plane length | Fail / orientation ambiguity |
| Small LED/button PCB width: 20.8 mm | Existing model assigns 20.8 mm to X | Pass if the small board is vertical; otherwise ambiguous |
| Large/main PCB width: 40.6 mm | Existing main PCB uses 40.6 mm in Z | Pass |
| Large/main PCB thickness: 1.14 mm | Existing PCB thickness is 1.14 mm | Pass |
| Full pack depth/cell depth reference: 43.9 mm | Existing total Y envelope is 54.89 mm | Fail |

## Validation conclusion

`cad/battery_pack.step` is **not acceptable as the locked master battery assembly** because it does not match the locked overall length, full pack depth, or controlled height envelope, and because at least one PCB dimension is assigned ambiguously relative to the requested locked measurement names.

A corrected battery-only model has therefore been created:

- `cad/battery_pack_v2.step`
- `cad/battery_pack_v2.stl`

The v2 model is still a simplified digital twin, not enclosure geometry. It includes only the battery assembly elements requested: six cells, plastic holder/carrier, main PCB, small LED/button PCB, DC jack, USB charging connector, pushbutton, LEDs, and a simple ribbon/connector clearance block.
