# Vacuum Battery Case V1 Assembly Notes

Version 1 is a test-fit enclosure generated from the simplified CAD reference model in `cad/step02_battery_assembly.step` / `cad/step02_battery_assembly.stl`.

## Fit assumptions

- Reference battery envelope used: approximately 96.7 mm × 56.86 mm × 55.2 mm.
- Internal clearance target: 0.8 mm per side.
- Wall/floor/lid thickness: 2.8 mm for FDM printing.
- The battery drops into the lower tray from above.
- The lid is a screw-secured cap with a shallow internal alignment lip.

## Openings

- USB-C opening is on the front / negative-Y wall of the lower half.
- Power button and LED openings are on the lid and are intentionally oversized for first test fitting.
- Verify exact port/button/LED positions against the real pack before any long print or production revision.

## Hardware

- Intended fasteners: M3 screws.
- Screw holes are modeled as 3.2 mm clearance holes.
- Four internal posts are included for lid retention.

## Printing

- Print the bottom with the flat base on the bed.
- Print the top with the outside face on the bed.
- Support should be minimal; the USB-C and indicator cutouts may bridge depending on slicer settings.
- Suggested first-test settings: 0.20 mm layer height, 3 perimeters, 20–30% infill.

## Revision guidance

This V1 is for fit/function only. Expect to adjust:

- USB-C cutout X/Z position.
- Power button and LED window positions.
- Screw post height and screw length.
- Split height if battery insertion or lid closure is tight.
