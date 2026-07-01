# Battery Pack Dimensions Report

## Measured dimensions used

| Item | Dimension | Value |
|---|---:|---:|
| Battery pack overall width | X envelope reference | 63.7 mm |
| Battery pack overall height | Z envelope reference | 63.1 mm |
| Battery pack overall depth | Y envelope reference | 43.9 mm |
| Cells | Count / type | 6 x 18650 |
| Cell diameter | Diameter | 18.3 mm |
| Cell length | Length | 65.0 mm |
| Cell arrangement | Columns x rows | 2 x 3 |
| Main PCB | Length x width | 95.0 mm x 40.6 mm |
| PCB thickness | Main and LED/button PCB | 1.14 mm |
| LED/button PCB | Height x width | 53.3 mm x 20.8 mm |

## Inferred dimensions and placements

- Axis mapping: cell length is modeled along X because the supplied 65.0 mm cell length aligns with the 63.7 mm overall pack width within measurement/scan interpretation tolerance better than with the 43.9 mm depth or 63.1 mm height.
- Two cell columns are distributed across the 43.9 mm depth, giving an inferred equal side/inter-column clearance of 2.433 mm.
- Three cell rows are distributed across the 63.1 mm height, giving an inferred equal top/bottom/inter-row clearance of 2.050 mm.
- The main PCB is centered on the front face as a measured 95.0 mm x 40.6 mm board; this exceeds the supplied 63.7 mm pack width, so the conflict is preserved rather than forced to fit.
- The LED/button PCB is centered on the rear face as a measured 53.3 mm x 20.8 mm board.

## Remaining unknown dimensions requiring verification

The following are named CAD parameters, not confirmed measurements:

| Parameter | Current model value | Verification needed |
|---|---:|---|
| `carrier_wall` | 1.6 mm | Measure from reference part/photos before release. |
| `carrier_rib` | 2.0 mm | Measure from reference part/photos before release. |
| `clip_lip` | 1.2 mm | Measure from reference part/photos before release. |
| `usb_c_w` | 8.94 mm | Measure from reference part/photos before release. |
| `usb_c_h` | 3.26 mm | Measure from reference part/photos before release. |
| `usb_c_d` | 7.35 mm | Measure from reference part/photos before release. |
| `button_w` | 6.0 mm | Measure from reference part/photos before release. |
| `button_h` | 3.5 mm | Measure from reference part/photos before release. |
| `button_d` | 2.5 mm | Measure from reference part/photos before release. |
| `ribbon_w` | 10.0 mm | Measure from reference part/photos before release. |
| `ribbon_t` | 0.35 mm | Measure from reference part/photos before release. |
| `led_d` | 3.0 mm | Measure from reference part/photos before release. |

## Output scope

- Retained `battery_pack.step` as the tracked CAD deliverable for the existing battery assembly.
- No enclosure, lid, battery box, or mounting brackets are included.
- The scan was not converted directly into mesh geometry; the model is rebuilt from named CAD primitives driven by the measured dimensions above.
