# Vacuum Battery Enclosure CAD

This task generates only the two-piece 3D-printable enclosure around the existing committed battery assembly STEP file.

## Reference input

- `cad/battery_pack.step` is the source of truth for the battery assembly.
- The battery assembly geometry is not regenerated or modified by this enclosure task.
- No `battery_pack.FCStd` file is created or tracked.

## Enclosure outputs

The generated enclosure deliverables are:

- `cad/enclosure_base.FCStd`
- `cad/enclosure_lid.FCStd`
- `cad/enclosure_base.step`
- `cad/enclosure_lid.step`
- `cad/enclosure_base.stl`
- `cad/enclosure_lid.stl`

## Enclosure design basis

The enclosure is derived from `cad/battery_pack.step` and uses:

- `0.3 mm` minimum clearance around the referenced assembly extents.
- `2.0 mm` wall thickness.
- `6.0 mm` corner-radius features.
- Four M3 screw boss axes for lid attachment.
- USB-C opening alignment from the committed `usb_c_connector` primitive.
- `5.0 mm` LED light-pipe axes from the committed LED primitive centers.
- Printed pushbutton actuator alignment from the committed `push_button` primitive.
- PCB support standoffs, battery locating ribs, and PCB-area ventilation features.

## Regeneration

If the enclosure must be regenerated, run:

```bash
python tools/build_enclosure.py
```

Do not run battery-pack generation as part of this enclosure-only task.
