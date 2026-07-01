"""Editable CadQuery model for the vacuum battery fit-check enclosure.

The model is driven by the committed scan ``6_30_2026.glb``.  It reads the GLB
accessor bounding box, scales the scan to millimetres, adds clearance, and then
builds an open-top tray with service cutouts observed in the reference photo set
(``drive-download-20260701T020457Z-3-001.zip``): charging module window, switch
slot, LED drill guides, and a USB-C opening.

Run with CadQuery installed:
    python cad/vacuum_battery_case.py
"""
from __future__ import annotations

import json
import struct
from pathlib import Path

import cadquery as cq
from cadquery import exporters

ROOT = Path(__file__).resolve().parents[1]
SCAN_PATH = ROOT / "6_30_2026.glb"
STL_PATH = ROOT / "output" / "vacuum_battery_fit_check_enclosure.stl"
STEP_PATH = ROOT / "output" / "vacuum_battery_fit_check_enclosure.step"

SCALE_MM_PER_SCAN_UNIT = 50.0
WALL = 2.4
FLOOR = 2.8
CLEARANCE = 1.5
MIN_INTERNAL_HEIGHT = 32.0
LIP_HEIGHT = 3.0
LIP_WALL = 1.2
CORNER_POST = 6.0
FILLET = 1.2

USB_C_WIDTH = 10.5
USB_C_HEIGHT = 4.2
USB_C_CENTER_Z = 10.0
CHARGE_MODULE_WIDTH = 28.0
CHARGE_MODULE_HEIGHT = 12.0
CHARGE_MODULE_CENTER_Z = 18.0
SWITCH_WIDTH = 14.0
SWITCH_HEIGHT = 7.0
SWITCH_CENTER_FROM_FRONT = 26.0
LED_DIAMETER = 3.2
LED_SPACING = 7.0
LED_COUNT = 4
LED_CENTER_X = -18.0


def scan_bbox(path: Path) -> tuple[list[float], list[float]]:
    """Return global VEC3 accessor min/max from a binary GLB scan."""
    data = path.read_bytes()
    magic, version, _length = struct.unpack_from("<III", data, 0)
    if magic != 0x46546C67 or version != 2:
        raise ValueError(f"{path} is not a GLB v2 file")
    offset = 12
    mins: list[list[float]] = []
    maxs: list[list[float]] = []
    while offset < len(data):
        chunk_len, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        chunk = data[offset : offset + chunk_len]
        offset += chunk_len
        if chunk_type == 0x4E4F534A:
            document = json.loads(chunk.decode("utf-8"))
            for accessor in document.get("accessors", []):
                if accessor.get("type") == "VEC3" and "min" in accessor and "max" in accessor:
                    mins.append(accessor["min"])
                    maxs.append(accessor["max"])
    if not mins:
        raise ValueError("No VEC3 accessor bounds found in scan")
    return [min(v[i] for v in mins) for i in range(3)], [max(v[i] for v in maxs) for i in range(3)]


def make_model() -> cq.Workplane:
    scan_min, scan_max = scan_bbox(SCAN_PATH)
    scan_x = (scan_max[0] - scan_min[0]) * SCALE_MM_PER_SCAN_UNIT
    scan_y = (scan_max[1] - scan_min[1]) * SCALE_MM_PER_SCAN_UNIT
    scan_z = (scan_max[2] - scan_min[2]) * SCALE_MM_PER_SCAN_UNIT

    inner_x = scan_x + 2 * CLEARANCE
    inner_z = scan_z + 2 * CLEARANCE
    inner_y = max(scan_y + 2 * CLEARANCE, MIN_INTERNAL_HEIGHT)
    outer_x = inner_x + 2 * WALL
    outer_z = inner_z + 2 * WALL
    outer_y = inner_y + FLOOR

    case = (
        cq.Workplane("XY")
        .box(outer_x, outer_z, outer_y, centered=(True, True, False))
        .faces(">Z")
        .shell(-WALL)
    )
    # Restore a thicker floor after shelling.
    case = case.union(cq.Workplane("XY").box(outer_x, outer_z, FLOOR, centered=(True, True, False)))

    front_y = -outer_z / 2
    right_x = outer_x / 2
    case = (
        case.faces("<Y").workplane(centerOption="CenterOfBoundBox")
        .center(0, USB_C_CENTER_Z - outer_y / 2)
        .rect(USB_C_WIDTH, USB_C_HEIGHT)
        .cutThruAll()
        .faces("<Y").workplane(centerOption="CenterOfBoundBox")
        .center(0, CHARGE_MODULE_CENTER_Z - outer_y / 2)
        .rect(CHARGE_MODULE_WIDTH, CHARGE_MODULE_HEIGHT)
        .cutThruAll()
    )
    case = (
        case.faces(">X").workplane(centerOption="CenterOfBoundBox")
        .center(SWITCH_CENTER_FROM_FRONT - outer_z / 2, FLOOR + inner_y * 0.55 - outer_y / 2)
        .rect(SWITCH_WIDTH, SWITCH_HEIGHT)
        .cutThruAll()
    )

    lip = (
        cq.Workplane("XY")
        .rect(inner_x, inner_z)
        .rect(inner_x - 2 * LIP_WALL, inner_z - 2 * LIP_WALL)
        .extrude(LIP_HEIGHT)
        .translate((0, 0, outer_y))
    )
    case = case.union(lip)

    for sx in (-1, 1):
        for sy in (-1, 1):
            post = cq.Workplane("XY").box(CORNER_POST, CORNER_POST, inner_y, centered=(True, True, False))
            post = post.translate((sx * (inner_x / 2 - CORNER_POST / 2), sy * (inner_z / 2 - CORNER_POST / 2), FLOOR))
            case = case.union(post)

    for i in range(LED_COUNT):
        x = LED_CENTER_X + (i - (LED_COUNT - 1) / 2) * LED_SPACING
        guide = cq.Workplane("XY").circle(LED_DIAMETER / 2).extrude(1.2).translate((x, front_y + WALL + 6.0, outer_y))
        case = case.union(guide)

    return case.edges("|Z").fillet(FILLET)


if __name__ == "__main__":
    STL_PATH.parent.mkdir(exist_ok=True)
    model = make_model()
    exporters.export(model, str(STL_PATH))
    exporters.export(model, str(STEP_PATH))
