# Battery Pack v2 Dimensions and Assumptions

## Locked measurements used

| Measurement | Value | How used in `battery_pack_v2` |
|---|---:|---|
| Cell count/type | Six 18650 cells | Six cylindrical cells are modelled. |
| Cell arrangement | 2 rows x 3 cells | Model uses two cells across depth (Y) and three stacked rows in height (Z). |
| Overall max assembly length | 96.7 mm | Overall X envelope is constrained to 96.7 mm. |
| Battery/cell block width | 63.7 mm | Plastic holder/carrier X envelope is constrained to 63.7 mm. |
| Battery/cell block height | 63.1 mm | Cell block/holder Z envelope is constrained to 63.1 mm. |
| Cell diameter | 18.3 mm | Each cell cylinder diameter is 18.3 mm. |
| Cell length | 65.0 mm | Each cell cylinder length is 65.0 mm. |
| Small LED/button PCB length | 53.3 mm | Small PCB long in-plane dimension is 53.3 mm along X. |
| Small LED/button PCB width | 20.8 mm | Small PCB short in-plane dimension is 20.8 mm along Z. |
| Large/main PCB width | 40.6 mm | Main PCB width is 40.6 mm along Z. |
| Large/main PCB thickness | 1.14 mm | Both PCB plates use 1.14 mm thickness. |
| Full pack depth/cell depth reference | 43.9 mm | Overall Y envelope is constrained to 43.9 mm. |

## Derived dimensions

| Derived dimension | Value | Formula / reason |
|---|---:|---|
| Two-cell depth side/inter-cell clearance | 2.433 mm | `(43.9 - 2 x 18.3) / 3`. |
| Three-cell height top/inter-row/bottom clearance | 2.050 mm | `(63.1 - 3 x 18.3) / 4`. |
| Cell Y centers | ±10.3667 mm | Places two 18.3 mm cells inside the 43.9 mm depth with equal clearance. |
| Cell Z centers | -20.35, 0.00, +20.35 mm | Places three 18.3 mm cells inside the 63.1 mm height with equal clearance. |
| Cell X overhang beyond 63.7 mm holder | 0.65 mm per side | 65.0 mm cell length exceeds the 63.7 mm locked battery/cell block width by 1.3 mm total. |
| Main PCB length | 96.7 mm | Inferred from the locked overall max assembly length because no separate large/main PCB length was provided. |
| Main PCB thickness direction | Y | Keeps the 1.14 mm PCB thickness normal to the pack face. |
| Main PCB width direction | Z | Uses the locked 40.6 mm board width as the vertical in-plane dimension. |
| Small PCB thickness direction | Y | Keeps the 1.14 mm PCB thickness normal to the opposite pack face. |
| Ribbon/connector clearance | 12.0 mm x 43.9 mm x 2.0 mm | Simple clearance-only volume; not a detailed connector. |

## Inferred component dimensions

These values are not locked caliper measurements. They are simple placeholders used only to make the requested assembly features spatially visible in the corrected CAD.

| Component / parameter | Inferred value |
|---|---:|
| Plastic holder end plate thickness | 0.65 mm |
| Plastic holder side rail thickness | 1.15 mm |
| Plastic holder cross rib thickness | 2.0 mm |
| DC jack outside diameter | 8.0 mm |
| DC jack model depth/length | 10.0 mm |
| USB charging connector width | 8.94 mm |
| USB charging connector height | 3.26 mm |
| USB charging connector depth | 7.35 mm |
| Pushbutton width | 6.0 mm |
| Pushbutton height | 3.5 mm |
| Pushbutton depth | 2.5 mm |
| LED diameter | 3.0 mm |
| Ribbon clearance width | 12.0 mm |
| Ribbon clearance height | 2.0 mm |

## Corrected model envelope

Parsed `cad/battery_pack_v2.stl` extents:

| Axis | Extent |
|---|---:|
| X / overall length | 96.7 mm |
| Y / full pack depth | 43.9 mm |
| Z / cell block height | 63.1 mm |

## Unresolved uncertainties

- Exact main PCB length was not separately listed; v2 uses the locked 96.7 mm overall maximum assembly length as the main PCB X extent.
- Exact main PCB placement relative to the cell holder is inferred from the scan/photo layout and kept within the locked overall envelope.
- Exact small LED/button PCB placement is inferred; only its 53.3 mm x 20.8 mm dimensions are locked.
- Exact DC jack size, connector barrel depth, and placement need caliper confirmation.
- Exact USB connector type and dimensions need caliper confirmation; v2 uses common USB-C-like simplified dimensions as visual clearance geometry.
- Exact pushbutton package dimensions and actuation protrusion need caliper confirmation.
- Exact LED count, package height, and lens protrusion need confirmation from the physical part/photos.
- Exact plastic holder rib thicknesses, clips, openings, and molded details are simplified and should be refined only after direct measurement.
- Ribbon cable and connector are represented as clearance geometry only, per scope.
- The Polycam GLB files are used for orientation/reference only because their embedded units are not millimetre-authenticated.

## Excluded by scope

No enclosure, lid, case, screw posts, openings, supports, vents, labels, or logos were created or modified for this correction.
