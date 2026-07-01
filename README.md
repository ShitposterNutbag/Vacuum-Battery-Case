# Vacuum Battery Assembly CAD Review Model

This repository is currently focused on modeling **only the battery assembly**
for dimensional verification. Tray and enclosure generation are intentionally
stopped until the measured battery assembly model is reviewed and approved.

## Authoritative references

- `6_30_2026v2.glb` is the cleaned scan used for holder/end-cap context and PCB
  side placement reference.
- The battery-cell pack is built from the uploaded measured specifications, not
  inferred from the scan mesh placement.
- The earlier `6_30_2026.glb` scan is retained but is not used for the current
  model.

## Measured cell-pack specification

- Cell type: six 18650 cells.
- Cell diameter: `18.0 mm`.
- Cell length: `68.9 mm`.
- Arrangement: `2 columns x 3 rows`.
- Cells are tangent to one another with `0.0 mm` intentional gap.
- Resulting measured pack envelope before holders/boards: `36.0 mm W x 68.9 mm D x 54.0 mm H`.

## Assembly-model assumptions

- The battery stands upright.
- The measured cells define the pack geometry; scan-derived battery placement is
  intentionally ignored.
- Battery holder/end caps and rails are retained as scan-observed context and
  sized around the measured tangent cell pack.
- Two vertical PCBs are mounted on opposite sides of the pack.
- Both PCBs are offset `2.0 mm` from the nearest battery surface.
- The long PCB is the primary face and includes the DC barrel jack, main power
  switch, connector, and wiring.
- The short PCB is on the opposite side and includes LED/button circuitry,
  connector, and wiring.

## Outputs

- `output/vacuum_battery_assembly_model.step` — STEP model for dimensional verification.
- `output/vacuum_battery_assembly_model.stl` — STL model generated from the same geometry.
- `output/vacuum_battery_assembly_model.json` — manifest documenting measured
  dimensions, scan scale, modeled components, and output files.
- `tools/generate_battery_assembly_model.py` — dependency-free generator for the
  assembly review STEP, STL, and manifest.

## Scope boundaries

This model includes the six measured/tangent cells, battery holder/end caps,
holder rails, both PCB boards, DC jack, main power switch, LED/button circuitry,
wiring, and connectors. It does **not** generate a fit-check tray, enclosure,
shell, or rectangular-prism placeholder. A tray should only be generated after
this assembly model is reviewed and approved.
