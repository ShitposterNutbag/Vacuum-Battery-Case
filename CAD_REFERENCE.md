# CAD Reference Model From Cleaned RealityScan Mesh

## Purpose and Scope

This document defines a **simplified CAD reference model** for the salvaged vacuum battery pack. It intentionally replaces noisy RealityScan surfaces with simple CAD-friendly keep-out geometry.

This is **not** the enclosure design. Do not offset these surfaces to make a case. Use this reference to plan clearances, port/window locations, and manual measurement work before enclosure modeling.

## Cleaned Mesh Analyzed

The cleanup workflow in `scripts/clean_realityscan_mesh.py` reads the RealityScan OBJ, removes the known tabletop and side protrusion artifacts, removes tiny floating components, caps resulting boundary loops, and exports watertight OBJ/STL reference meshes.

Validation run used for this reference:

```text
source_vertices=13301 source_faces=22089
cleaned_vertices=12500 cleaned_faces=24688
nonmanifold_edges=0 boundary_edges=0
```

Measured cleaned-mesh bounding box in mesh coordinates, converted to millimetres:

| Axis | Minimum | Maximum | Span |
| --- | ---: | ---: | ---: |
| X | -160.609 mm | 124.599 mm | 285.208 mm |
| Y | 60.176 mm | 333.437 mm | 273.261 mm |
| Z | -266.145 mm | 176.042 mm | 442.187 mm |

The absolute scan orientation is treated as arbitrary. The simplified reference model normalizes the minimum cleaned-mesh corner to `[0, 0, 0]` and preserves the overall cleaned-mesh envelope spans above.

## Reference CAD Deliverable

The simplified model is provided as:

- `cad/cad_reference_model.scad`

OpenSCAD is used because it is readable, parametric text CAD and can be revised easily after manual measurements. The model contains only reference/keep-out geometry:

- translucent overall cleaned-mesh envelope
- simplified six-cell battery block
- main PCB keep-out slab
- USB-C charging board slab and port marker
- power-button marker
- LED marker row

## Major Geometric Features Identified

### Battery Cell Block

The cleaned mesh preserves the dominant battery mass. The reference model represents this as six tangent cylindrical cells in a compact block. The cylinders are not intended to reproduce scan roughness or wrapper texture. They are a keep-out proxy for the rechargeable cell cluster.

Assumption: the pack is a six-cell 18650-style block because the existing repository CAD already contains a six-cell 18650 reference. The exact cell diameter, length, count, and pitch must still be checked manually before enclosure design.

### PCB

The PCB is represented as a thin rectangular board keep-out on the electronics side of the pack. Small components, solder blobs, wire bends, and scan noise are intentionally omitted. Treat the slab as the minimum board keep-out, then add measured component heights before designing a lid or ribs.

### USB-C Charging Board

The USB-C charging board is represented as a smaller rectangular board mounted near the outward electronics face, with a black rectangular USB-C port/opening marker. The marker is only a location cue for a future enclosure cutout.

### Power Button

The power button is represented as a circular protrusion marker on the outward electronics face. The enclosure design should later define button clearance, travel clearance, tactile access, and support geometry from manual measurements.

### LED Locations

The LEDs are represented as a row of four small circular markers. The count and spacing are reference assumptions from the visible indicator region and must be verified manually. Future enclosure work should use measured LED center locations and decide between individual holes, a light pipe, or a translucent window.

## Sketches and Assumptions

### Normalized Reference Coordinate System

```text
Cleaned mesh min corner becomes CAD origin.

          +Y / electronics face
          ↑
          │     PCB, USB-C board, button, LEDs
          │     are modeled near this outward face
          │
          └────────────→ +X
         ╱
        ╱ +Z / long scan-depth span
```

### Top-Level Keep-Out Sketch

```text
Transparent bounding box = cleaned mesh envelope

+--------------------------------------------------+
|                                                  |
|        [ LED LED LED LED ]   (POWER BUTTON)      |  electronics face
|              +----------------------+            |
|              | USB-C CHARGER BOARD  |            |
|              +----------------------+            |
|        +--------------------------------+         |
|        |              PCB               |         |
|        +--------------------------------+         |
|                                                  |
|   O====O====O                                     |
|   O====O====O        six-cell block proxy         |
|                                                  |
+--------------------------------------------------+
```

### Section Assumption Sketch

```text
Future enclosure must clear the tallest actual component, not just the PCB slab.

     enclosure lid NOT DESIGNED YET
   ─────────────────────────────────
         manual clearance TBD
        ↑
  [button] [LEDs] [USB-C port]
  ┌──────────────────────────────┐
  │ PCB / charging board keepout │
  └──────────────────────────────┘
  ╭────────╮ ╭────────╮ ╭────────╮
  │ cell   │ │ cell   │ │ cell   │
  ╰────────╯ ╰────────╯ ╰────────╯
```

## Recommended Modeling Strategy

1. Keep the cleaned mesh as an underlay/reference only.
2. Use `cad/cad_reference_model.scad` as the editable dimensional skeleton.
3. Replace each assumed feature dimension with caliper measurements before enclosure work.
4. Lock the battery cell block first, because it drives the main cavity and retention strategy.
5. Lock the PCB and charging-board keep-outs second, including maximum component height.
6. Lock external interface datums last: USB-C port center, button center, and LED centers relative to the cell block.
7. Only after those datums are verified, start a separate enclosure model with deliberate clearances.
8. Do not mesh-offset the RealityScan surface. Build the enclosure from clean primitives, sketches, constraints, and measured dimensions.

## Critical Dimensions to Measure Manually Before Enclosure Design

Measure these with calipers and record the datum used for each measurement.

### Overall Pack and Cell Block

- Overall physical length, width, and height of the pack after removing tape/scan artifacts.
- Cell diameter and cell length.
- Number of cells, row/column arrangement, and center-to-center pitch.
- Cell block outer envelope including weld tabs, insulation, wrappers, and wires.
- Highest and lowest points of the physical pack when resting in the intended enclosure orientation.

### PCB and Electronics

- Main PCB length, width, thickness, and corner locations relative to the cell block.
- Maximum component height above both sides of the PCB.
- Wire routing envelope and minimum bend radius.
- Any fragile components or solder joints that must not contact the enclosure.

### USB-C Charging Board

- Charging board length, width, thickness, and exact position relative to the main pack datum.
- USB-C receptacle shell width, height, depth, and centerline.
- Distance from USB-C receptacle face to the nearest stable pack datum.
- Required plug insertion clearance around the port, including cable overmold clearance.

### Power Button

- Button cap diameter or rectangular outline.
- Button center location relative to USB-C port center and pack datum.
- Button protrusion height above nearby board/pack surfaces.
- Required actuation travel and side clearance.

### LEDs

- LED count.
- LED center-to-center spacing.
- LED center positions relative to USB-C port center, button center, and pack datum.
- LED viewing direction and whether a window or light pipe is preferred.
- Required clearance above LED packages.

### Enclosure-Planning Clearances

- Minimum clearance for easy insertion/removal of the battery pack.
- Local clearance around solder joints, tabs, and wires.
- Wall thickness target for FDM printing.
- Screw, snap, or strap locations that avoid cells, PCB traces, and wires.
- Ventilation or heat-relief requirements, if the pack warms during charging/discharge.

## Open Items

- The scan scale and coordinate orientation should be confirmed against at least one caliper-measured physical dimension.
- The LED count and exact indicator spacing are assumed placeholders until measured.
- The simplified reference should be updated before enclosure design begins.
