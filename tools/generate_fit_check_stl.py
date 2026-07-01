#!/usr/bin/env python3
"""Generate the open-top fit-check tray STL from the cleaned GLB scan.

This intentionally creates only a simple test-fit tray, not a final enclosure.
The battery stands upright with the scan's X axis as width, Z axis as height,
and Y axis as PCB-to-PCB depth.  The long PCB is assigned to the front/primary
face; only that side receives coarse fit-check reliefs for the DC barrel jack
and main power button.  The opposite short-PCB side is left without functional
button openings.

No third-party packages are required.
"""
from __future__ import annotations

import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN = ROOT / "6_30_2026v2.glb"
OUT = ROOT / "output" / "vacuum_battery_fit_check_tray.stl"
LEGACY_OUT = ROOT / "output" / "vacuum_battery_fit_check_enclosure.stl"

SCALE_MM_PER_SCAN_UNIT = 50.0
WALL = 2.4
FLOOR = 2.8
CLEARANCE = 1.5
MIN_INTERNAL_DEPTH = 22.0
FRONT_WALL_HEIGHT = 18.0
BACK_WALL_HEIGHT = 22.0
SIDE_WALL_HEIGHT = 36.0
CORNER_POST = 6.0

# Coarse long-PCB fit-check reliefs only; not final feature geometry.
DC_JACK_RELIEF = dict(center_x=0.0, center_z=13.0, width=16.0, height=12.0)
MAIN_POWER_RELIEF = dict(center_x=26.0, center_z=24.0, width=18.0, height=10.0)


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


def box_triangles(cx: float, cy: float, cz: float, sx: float, sy: float, sz: float):
    x0, x1 = cx - sx / 2, cx + sx / 2
    y0, y1 = cy - sy / 2, cy + sy / 2
    z0, z1 = cz - sz / 2, cz + sz / 2
    v = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    faces = [(0,1,2),(0,2,3),(4,6,5),(4,7,6),(0,4,5),(0,5,1),(1,5,6),(1,6,2),(2,6,7),(2,7,3),(3,7,4),(3,4,0)]
    return [(v[a], v[b], v[c]) for a, b, c in faces]


def add_front_wall_with_reliefs(tris, y_pos: float, width: float, height: float, thick: float, reliefs: list[dict[str, float]]):
    # Wall spans X/Z at constant Y.  Reliefs are rectangles in X/Z.
    z_intervals = [(0.0, height)]
    for relief in reliefs:
        rz0 = relief["center_z"] - relief["height"] / 2
        rz1 = relief["center_z"] + relief["height"] / 2
        split = []
        for z0, z1 in z_intervals:
            if rz0 > z0:
                split.append((z0, min(z1, rz0)))
            if rz1 < z1:
                split.append((max(z0, rz1), z1))
        z_intervals = [pair for pair in split if pair[1] - pair[0] > 0.1]
    for z0, z1 in z_intervals:
        x_edges = [-width / 2]
        for relief in reliefs:
            rz0 = relief["center_z"] - relief["height"] / 2
            rz1 = relief["center_z"] + relief["height"] / 2
            if not (z1 <= rz0 or z0 >= rz1):
                x_edges += [relief["center_x"] - relief["width"] / 2, relief["center_x"] + relief["width"] / 2]
        x_edges += [width / 2]
        x_edges = sorted(x_edges)
        for x0, x1 in zip(x_edges, x_edges[1:]):
            blocked = any(
                x0 >= r["center_x"] - r["width"] / 2 - 0.01
                and x1 <= r["center_x"] + r["width"] / 2 + 0.01
                and not (z1 <= r["center_z"] - r["height"] / 2 or z0 >= r["center_z"] + r["height"] / 2)
                for r in reliefs
            )
            if not blocked and x1 - x0 > 0.1:
                tris += box_triangles((x0 + x1) / 2, y_pos, (z0 + z1) / 2, x1 - x0, thick, z1 - z0)


def write_stl(tris, path: Path):
    def normal(a, b, c):
        ux, uy, uz = [b[i] - a[i] for i in range(3)]
        vx, vy, vz = [c[i] - a[i] for i in range(3)]
        n = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
        length = math.sqrt(sum(i * i for i in n)) or 1.0
        return tuple(i / length for i in n)
    with path.open("w") as f:
        f.write("solid vacuum_battery_fit_check_tray\n")
        for a, b, c in tris:
            n = normal(a, b, c)
            f.write(f" facet normal {n[0]:.6g} {n[1]:.6g} {n[2]:.6g}\n  outer loop\n")
            for point in (a, b, c):
                f.write(f"   vertex {point[0]:.6g} {point[1]:.6g} {point[2]:.6g}\n")
            f.write("  endloop\n endfacet\n")
        f.write("endsolid vacuum_battery_fit_check_tray\n")


def main():
    scan_min, scan_max = scan_bbox(SCAN)
    scan_width = (scan_max[0] - scan_min[0]) * SCALE_MM_PER_SCAN_UNIT
    scan_depth = (scan_max[1] - scan_min[1]) * SCALE_MM_PER_SCAN_UNIT
    scan_height = (scan_max[2] - scan_min[2]) * SCALE_MM_PER_SCAN_UNIT

    inner_width = scan_width + 2 * CLEARANCE
    inner_depth = max(scan_depth + 2 * CLEARANCE, MIN_INTERNAL_DEPTH)
    outer_width = inner_width + 2 * WALL
    outer_depth = inner_depth + 2 * WALL

    tris = []
    tris += box_triangles(0, 0, -FLOOR / 2, outer_width, outer_depth, FLOOR)
    add_front_wall_with_reliefs(
        tris,
        -outer_depth / 2 + WALL / 2,
        outer_width,
        FRONT_WALL_HEIGHT,
        WALL,
        [DC_JACK_RELIEF, MAIN_POWER_RELIEF],
    )
    tris += box_triangles(0, outer_depth / 2 - WALL / 2, BACK_WALL_HEIGHT / 2, outer_width, WALL, BACK_WALL_HEIGHT)
    tris += box_triangles(-outer_width / 2 + WALL / 2, 0, SIDE_WALL_HEIGHT / 2, WALL, outer_depth, SIDE_WALL_HEIGHT)
    tris += box_triangles(outer_width / 2 - WALL / 2, 0, SIDE_WALL_HEIGHT / 2, WALL, outer_depth, SIDE_WALL_HEIGHT)
    for sx in (-1, 1):
        for sy in (-1, 1):
            tris += box_triangles(
                sx * (inner_width / 2 - CORNER_POST / 2),
                sy * (inner_depth / 2 - CORNER_POST / 2),
                SIDE_WALL_HEIGHT / 2,
                CORNER_POST,
                CORNER_POST,
                SIDE_WALL_HEIGHT,
            )

    OUT.parent.mkdir(exist_ok=True)
    write_stl(tris, OUT)
    if LEGACY_OUT.exists():
        LEGACY_OUT.unlink()
    print(
        f"wrote {OUT} outer {outer_width:.1f} x {outer_depth:.1f} x {SIDE_WALL_HEIGHT:.1f} mm; "
        f"cleaned scan bbox {scan_width:.1f} W x {scan_depth:.1f} D x {scan_height:.1f} H mm"
    )


if __name__ == "__main__":
    main()
