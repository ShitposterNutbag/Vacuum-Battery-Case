# Vacuum Battery Case

Parametric CadQuery first fit-check enclosure for an existing vacuum battery pack/BMS assembly plus a separate USB power-bank module.

## Current status

The uploaded 3D scan and reference-photo ZIP were not present in this checkout, so the scan was not converted and no photo-derived port positions were guessed. The current model uses only the supplied approximate envelope and includes configurable placeholders for final measured cutout locations.

See `docs/missing_measurements.md` for the exact measurements still needed before DC barrel jack, USB-A, micro-USB, LED, and pushbutton cutouts can be safely opened. See `reference_assets.md` for the asset retrieval status in this environment.

## Generate exports

```bash
python -m pip install -r requirements.txt
python models/vacuum_battery_case.py
# or, after measured feature locations are available:
python models/vacuum_battery_case.py --params measured_cutouts.json --out exports
```

Expected outputs:

- `exports/vacuum_battery_case_base.step`
- `exports/vacuum_battery_case_lid.step`
- `exports/vacuum_battery_case_base.stl`
- `exports/vacuum_battery_case_lid.stl`
