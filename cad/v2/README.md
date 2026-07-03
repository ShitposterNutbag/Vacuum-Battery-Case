# Vacuum Battery Case V2

This revision is an OpenSCAD source-only update for the battery case. No STL, OBJ, PNG, JPG, GLB, or other binary export is included for V2.

## Verification checklist

- `battery_case_v2.scad` exists in this directory.
- The DC jack opening is on the short side wall, specifically the `-X` wall.
- The DC jack opening is 9.5 mm wide by 7.5 mm high.
- The DC jack opening starts 2 mm above the outside bottom of the case.
- The four V1 screw posts are removed; V2 contains no post geometry.
- V2 defines exactly two internal rails.
- Each rail is 9.5 mm tall, inset 12 mm from the side walls, and runs the usable internal length of the case.

## Source notes

The OpenSCAD file keeps these dimensions as named variables so the checklist can be verified directly from source without exporting mesh files or preview images.
