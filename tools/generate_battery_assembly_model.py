#!/usr/bin/env python3
"""Generate a review CAD model of the battery assembly only.

The model is based on the cleaned scan ``6_30_2026v2.glb`` scaled to the
caliper-photo reference of 50.0 mm per scan unit.  It intentionally models the
battery assembly components only: six cells, holders, long and short PCBs, DC
jack, main power button, wiring, and board connectors.  It does not generate a
tray, enclosure, shell, or rectangular placeholder block.

The output is a triangulated STL review model suitable for checking relative
feature locations before any fit-check tray work resumes.
"""
from __future__ import annotations

import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN = ROOT / "6_30_2026v2.glb"
OUT = ROOT / "output" / "vacuum_battery_assembly_model.stl"
MANIFEST = ROOT / "output" / "vacuum_battery_assembly_model.json"

SCALE_MM_PER_SCAN_UNIT = 50.0

# Scan-derived upright envelope, with X=width, Y=PCB-to-PCB depth, Z=height.
# Dimensions are computed at runtime from the cleaned GLB bbox.
CELL_DIAMETER = 18.4
CELL_LENGTH = 65.2
CELL_SPACING_X = 20.2
CELL_SPACING_Z = 39.0
CELL_SEGMENTS = 32
WIRE_DIAMETER = 2.2
WIRE_SEGMENTS = 12
BOARD_THICKNESS = 1.6
LONG_PCB_WIDTH = 18.0
SHORT_PCB_WIDTH = 16.0
PCB_HEIGHT = 92.0
HOLDER_THICKNESS = 2.0
HOLDER_RAIL_WIDTH = 5.0

DC_JACK = dict(x=-18.0, z=82.0, diameter=9.5, length=12.0)
MAIN_POWER_BUTTON = dict(x=24.0, z=58.0, width=12.0, height=7.0, protrusion=3.0)
LONG_BOARD_CONNECTOR = dict(x=-37.0, z=31.0, width=9.0, height=8.0, protrusion=4.0)
SHORT_BOARD_CONNECTOR = dict(x=34.0, z=34.0, width=10.0, height=7.0, protrusion=3.0)
LED_POSITIONS = [(-18.0, 64.0), (-10.0, 64.0), (-2.0, 64.0), (6.0, 64.0)]
VACUUM_MODE_BUTTON = dict(x=19.0, z=58.0, width=7.0, height=5.0, protrusion=1.8)


def scan_bbox(path: Path) -> tuple[list[float], list[float]]:
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


def add_box(tris, cx, cy, cz, sx, sy, sz):
    x0, x1 = cx - sx / 2, cx + sx / 2
    y0, y1 = cy - sy / 2, cy + sy / 2
    z0, z1 = cz - sz / 2, cz + sz / 2
    v = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    faces = [(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    tris.extend((v[a], v[b], v[c]) for a, b, c in faces)


def add_cylinder_x(tris, cx, cy, cz, length, radius, segments=CELL_SEGMENTS):
    x0, x1 = cx - length / 2, cx + length / 2
    left_center = (x0, cy, cz)
    right_center = (x1, cy, cz)
    for i in range(segments):
        a0 = 2 * math.pi * i / segments
        a1 = 2 * math.pi * (i + 1) / segments
        p0 = (x0, cy + radius * math.cos(a0), cz + radius * math.sin(a0))
        p1 = (x0, cy + radius * math.cos(a1), cz + radius * math.sin(a1))
        p2 = (x1, cy + radius * math.cos(a1), cz + radius * math.sin(a1))
        p3 = (x1, cy + radius * math.cos(a0), cz + radius * math.sin(a0))
        tris.extend([(p0, p1, p2), (p0, p2, p3), (left_center, p1, p0), (right_center, p3, p2)])


def add_cylinder_y(tris, cx, cy, cz, length, radius, segments=24):
    y0, y1 = cy - length / 2, cy + length / 2
    front_center = (cx, y0, cz)
    back_center = (cx, y1, cz)
    for i in range(segments):
        a0 = 2 * math.pi * i / segments
        a1 = 2 * math.pi * (i + 1) / segments
        p0 = (cx + radius * math.cos(a0), y0, cz + radius * math.sin(a0))
        p1 = (cx + radius * math.cos(a1), y0, cz + radius * math.sin(a1))
        p2 = (cx + radius * math.cos(a1), y1, cz + radius * math.sin(a1))
        p3 = (cx + radius * math.cos(a0), y1, cz + radius * math.sin(a0))
        tris.extend([(p0, p2, p1), (p0, p3, p2), (front_center, p0, p1), (back_center, p2, p3)])


def add_wire_segment(tris, start, end, diameter=WIRE_DIAMETER):
    # Rectangular-prism wire segment, adequate for relative connector routing review.
    x0, y0, z0 = start
    x1, y1, z1 = end
    dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-6:
        return
    # For this model, wires are routed mostly in X/Z on board faces; use an axis-aligned
    # bounding prism around each path segment to keep the STL dependency-free.
    add_box(
        tris,
        (x0 + x1) / 2,
        (y0 + y1) / 2,
        (z0 + z1) / 2,
        max(abs(dx), diameter),
        max(abs(dy), diameter),
        max(abs(dz), diameter),
    )


def add_board_features(tris, y_front, y_back):
    # Long PCB, primary face.
    add_box(tris, 0, y_front, 63, 82, BOARD_THICKNESS, PCB_HEIGHT)
    add_cylinder_y(tris, DC_JACK["x"], y_front - DC_JACK["length"] / 2, DC_JACK["z"], DC_JACK["length"], DC_JACK["diameter"] / 2)
    add_box(tris, MAIN_POWER_BUTTON["x"], y_front - MAIN_POWER_BUTTON["protrusion"] / 2, MAIN_POWER_BUTTON["z"], MAIN_POWER_BUTTON["width"], MAIN_POWER_BUTTON["protrusion"], MAIN_POWER_BUTTON["height"])
    add_box(tris, LONG_BOARD_CONNECTOR["x"], y_front - LONG_BOARD_CONNECTOR["protrusion"] / 2, LONG_BOARD_CONNECTOR["z"], LONG_BOARD_CONNECTOR["width"], LONG_BOARD_CONNECTOR["protrusion"], LONG_BOARD_CONNECTOR["height"])

    # Short PCB, secondary face.  Includes LEDs and vacuum mode button for review,
    # but the button is intentionally not an enclosure/tray cutout target.
    add_box(tris, 0, y_back, 62, 58, BOARD_THICKNESS, 62)
    for x, z in LED_POSITIONS:
        add_cylinder_y(tris, x, y_back + 1.4, z, 2.8, 1.7, segments=16)
    add_box(tris, VACUUM_MODE_BUTTON["x"], y_back + VACUUM_MODE_BUTTON["protrusion"] / 2, VACUUM_MODE_BUTTON["z"], VACUUM_MODE_BUTTON["width"], VACUUM_MODE_BUTTON["protrusion"], VACUUM_MODE_BUTTON["height"])
    add_box(tris, SHORT_BOARD_CONNECTOR["x"], y_back + SHORT_BOARD_CONNECTOR["protrusion"] / 2, SHORT_BOARD_CONNECTOR["z"], SHORT_BOARD_CONNECTOR["width"], SHORT_BOARD_CONNECTOR["protrusion"], SHORT_BOARD_CONNECTOR["height"])


def make_model():
    scan_min, scan_max = scan_bbox(SCAN)
    scan_width = (scan_max[0] - scan_min[0]) * SCALE_MM_PER_SCAN_UNIT
    scan_depth = (scan_max[1] - scan_min[1]) * SCALE_MM_PER_SCAN_UNIT
    scan_height = (scan_max[2] - scan_min[2]) * SCALE_MM_PER_SCAN_UNIT

    y_front = -scan_depth / 2 - BOARD_THICKNESS / 2
    y_back = scan_depth / 2 + BOARD_THICKNESS / 2
    tris = []

    # Six-cell pack: two columns by three rows, upright in the scan envelope.
    cell_z0 = 24.0
    for row in range(3):
        for col in range(2):
            x = (col - 0.5) * CELL_SPACING_X
            z = cell_z0 + row * CELL_SPACING_Z
            add_cylinder_x(tris, x, 0, z, CELL_LENGTH, CELL_DIAMETER / 2)

    # Battery holders/rails around the cell group.
    holder_width = CELL_LENGTH + 10.0
    for z in (cell_z0 - 13.0, cell_z0 + CELL_SPACING_Z, cell_z0 + 2 * CELL_SPACING_Z + 13.0):
        add_box(tris, 0, 0, z, holder_width, HOLDER_THICKNESS, HOLDER_RAIL_WIDTH)
    for x in (-holder_width / 2, holder_width / 2):
        add_box(tris, x, 0, cell_z0 + CELL_SPACING_Z, HOLDER_THICKNESS, HOLDER_THICKNESS, 2 * CELL_SPACING_Z + 30.0)

    add_board_features(tris, y_front, y_back)

    # Wiring/connectors between pack and boards.
    add_wire_segment(tris, (-32, y_front - 1.5, 31), (-32, -2, 42))
    add_wire_segment(tris, (-32, -2, 42), (-20, 0, 54))
    add_wire_segment(tris, (34, y_back + 1.5, 34), (26, 2, 47))
    add_wire_segment(tris, (26, 2, 47), (18, 0, 72))
    add_wire_segment(tris, (-18, y_front - 2.0, 82), (-7, 0, 101))

    return tris, (scan_width, scan_depth, scan_height)


def write_stl(tris, path: Path):
    def normal(a, b, c):
        ux, uy, uz = [b[i] - a[i] for i in range(3)]
        vx, vy, vz = [c[i] - a[i] for i in range(3)]
        n = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
        length = math.sqrt(sum(i * i for i in n)) or 1.0
        return tuple(i / length for i in n)
    with path.open("w") as f:
        f.write("solid vacuum_battery_assembly_model\n")
        for a, b, c in tris:
            n = normal(a, b, c)
            f.write(f" facet normal {n[0]:.6g} {n[1]:.6g} {n[2]:.6g}\n  outer loop\n")
            for p in (a, b, c):
                f.write(f"   vertex {p[0]:.6g} {p[1]:.6g} {p[2]:.6g}\n")
            f.write("  endloop\n endfacet\n")
        f.write("endsolid vacuum_battery_assembly_model\n")


def main():
    tris, dims = make_model()
    OUT.parent.mkdir(exist_ok=True)
    write_stl(tris, OUT)
    manifest = {
        "source_scan": str(SCAN.relative_to(ROOT)),
        "scale_mm_per_scan_unit": SCALE_MM_PER_SCAN_UNIT,
        "scan_bbox_mm": {"width_x": round(dims[0], 3), "depth_y": round(dims[1], 3), "height_z": round(dims[2], 3)},
        "modeled_components": [
            "six cylindrical cells",
            "battery holder rails",
            "long PCB with DC jack, main power button, and connector",
            "short PCB with LEDs, vacuum mode button, and connector",
            "wire segments between boards and cell pack",
        ],
        "long_pcb_primary_face": "negative Y/front",
        "short_pcb_secondary_face": "positive Y/back",
        "no_tray_or_enclosure_generated": True,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"wrote {OUT} and {MANIFEST} with {len(tris)} facets; "
        f"cleaned scan bbox {dims[0]:.1f} W x {dims[1]:.1f} D x {dims[2]:.1f} H mm"
    )


if __name__ == "__main__":
    main()
