# Missing measurements for port/window finalization

The uploaded scan and eight grid-paper reference photos were not present in `/workspace/Vacuum-Battery-Case` when this model was generated, so the scan could not be used as reference geometry and the photos could not be reviewed for feature locations.

No feature locations were guessed. The first fit-check model therefore includes the known battery envelope, wall/clearance allowances, locating ribs, wire-routing channels, lid magnets, and removable lid, but leaves configurable placeholder parameters for external cutouts.

Please provide these measurements in millimeters from the inside lower-left-front corner of the battery cavity, using axes documented in `models/vacuum_battery_case.py`:

1. DC barrel jack center: X, Y, Z; jack outer diameter; required panel opening diameter; side of enclosure.
2. USB-A port center: X, Y, Z; opening width; opening height; side of enclosure.
3. Micro-USB port center: X, Y, Z; opening width; opening height; side of enclosure.
4. BMS LED window: X, Y, Z or LED group bounding box; window width; window height; side of enclosure.
5. BMS pushbutton: X, Y, Z; button/plunger diameter; access-hole diameter; side of enclosure.
6. USB power-bank module PCB envelope and mounting location relative to the battery pack/BMS assembly.
7. Wire exit/entry points between the BMS board and USB module, if wire routing must avoid specific components.

Known dimensions used:

- Battery assembly envelope: 100 mm × 69.3 mm × 40 mm.
- Nominal wall thickness: 2 mm.
- Battery clearance: 0.5 mm per side.
- Lid magnet pockets: 10 mm diameter × 3 mm deep.
