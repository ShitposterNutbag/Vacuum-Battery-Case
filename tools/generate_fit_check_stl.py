#!/usr/bin/env python3
"""Generate the v2 vacuum battery fit-check tray STL without third-party packages.

The committed GLB scan and photo ZIP are visual references only for v2.  The STL
is generated from the authoritative measured dimensions in vacuum_battery_case_v2.py.
"""
from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "vacuum_battery_fit_check_v2.stl"

OUTER_LENGTH = 104.0
OUTER_WIDTH = 72.5
OUTER_HEIGHT = 67.5
INTERNAL_LENGTH = 99.0
INTERNAL_WIDTH = 67.5
INTERNAL_HEIGHT = 63.0
WALL = 2.5
FLOOR = 2.5

DC_JACK = (52.0, 10.5, 13.0, 10.0)  # center_x_from_left, center_z, width, height
POWER_BUTTON = (41.0, 23.0, 9.0, 7.0)
LED_COUNT = 4
LED_CENTER_X = 52.0
LED_CENTER_Z = 59.0
LED_SPACING = 7.0
LED_WINDOW_WIDTH = 4.0
LED_WINDOW_HEIGHT = 2.5
PCB_POST_SIZE = 5.0
PCB_POST_HEIGHT = 12.0
PCB_POST_X_OFFSETS = (-16.0, 16.0)
PCB_POST_Y_OFFSETS = (-18.0, -6.0)


def centered_x(x_from_left: float) -> float:
    return x_from_left - OUTER_LENGTH / 2.0


def normal(a, b, c):
    ux, uy, uz = (b[i] - a[i] for i in range(3))
    vx, vy, vz = (c[i] - a[i] for i in range(3))
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    length = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return nx / length, ny / length, nz / length


def quad(tris, a, b, c, d):
    tris.append((a, b, c))
    tris.append((a, c, d))


def box(tris, x0, x1, y0, y1, z0, z1, omit_bottom=False):
    if not omit_bottom:
        quad(tris, (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0))
    quad(tris, (x0, y0, z1), (x0, y1, z1), (x1, y1, z1), (x1, y0, z1))
    quad(tris, (x0, y0, z0), (x0, y0, z1), (x1, y0, z1), (x1, y0, z0))
    quad(tris, (x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0))
    quad(tris, (x1, y1, z0), (x1, y1, z1), (x0, y1, z1), (x0, y1, z0))
    quad(tris, (x0, y1, z0), (x0, y1, z1), (x0, y0, z1), (x0, y0, z0))


def panel_with_windows(tris, y0, y1, z0, z1, windows):
    """Create an X/Z side wall panel with rectangular openings."""
    x0, x1 = -OUTER_LENGTH / 2.0, OUTER_LENGTH / 2.0
    z_breaks = {z0, z1}
    for cx, cz, width, height in windows:
        z_breaks.add(cz - height / 2.0)
        z_breaks.add(cz + height / 2.0)
    z_values = sorted(z_breaks)
    for za, zb in zip(z_values, z_values[1:]):
        if zb <= z0 or za >= z1:
            continue
        xa_values = {x0, x1}
        active = []
        for cx, cz, width, height in windows:
            if not (zb <= cz - height / 2.0 or za >= cz + height / 2.0):
                active.append((cx, width))
                xa_values.add(cx - width / 2.0)
                xa_values.add(cx + width / 2.0)
        xs = sorted(xa_values)
        for xa, xb in zip(xs, xs[1:]):
            blocked = any(xa >= cx - width / 2.0 - 1e-6 and xb <= cx + width / 2.0 + 1e-6 for cx, width in active)
            if not blocked and xb - xa > 1e-6 and zb - za > 1e-6:
                box(tris, xa, xb, y0, y1, za, zb)


def write_stl(tris):
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as stream:
        stream.write("solid vacuum_battery_fit_check_v2\n")
        for a, b, c in tris:
            nx, ny, nz = normal(a, b, c)
            stream.write(f" facet normal {nx:.7g} {ny:.7g} {nz:.7g}\n  outer loop\n")
            for x, y, z in (a, b, c):
                stream.write(f"   vertex {x:.7g} {y:.7g} {z:.7g}\n")
            stream.write("  endloop\n endfacet\n")
        stream.write("endsolid vacuum_battery_fit_check_v2\n")


def main():
    tris = []
    x0, x1 = -OUTER_LENGTH / 2.0, OUTER_LENGTH / 2.0
    y0, y1 = -OUTER_WIDTH / 2.0, OUTER_WIDTH / 2.0
    ix0, ix1 = -INTERNAL_LENGTH / 2.0, INTERNAL_LENGTH / 2.0
    iy0, iy1 = -INTERNAL_WIDTH / 2.0, INTERNAL_WIDTH / 2.0

    # Floor and four walls.  Top remains open for first-fit checking.
    box(tris, x0, x1, y0, y1, 0.0, FLOOR)
    panel_with_windows(
        tris,
        y0,
        y0 + WALL,
        FLOOR,
        OUTER_HEIGHT,
        [
            (centered_x(DC_JACK[0]), DC_JACK[1], DC_JACK[2], DC_JACK[3]),
            (centered_x(POWER_BUTTON[0]), POWER_BUTTON[1], POWER_BUTTON[2], POWER_BUTTON[3]),
        ],
    )
    led_start = LED_CENTER_X - (LED_COUNT - 1) * LED_SPACING / 2.0
    panel_with_windows(
        tris,
        y1 - WALL,
        y1,
        FLOOR,
        OUTER_HEIGHT,
        [
            (centered_x(led_start + idx * LED_SPACING), LED_CENTER_Z, LED_WINDOW_WIDTH, LED_WINDOW_HEIGHT)
            for idx in range(LED_COUNT)
        ],
    )
    box(tris, x0, x0 + WALL, iy0, iy1, FLOOR, OUTER_HEIGHT)
    box(tris, x1 - WALL, x1, iy0, iy1, FLOOR, OUTER_HEIGHT)

    # Four charging PCB support posts, connected to the floor and raised for jack clearance.
    for cx in PCB_POST_X_OFFSETS:
        for cy in PCB_POST_Y_OFFSETS:
            half = PCB_POST_SIZE / 2.0
            box(tris, cx - half, cx + half, cy - half, cy + half, FLOOR, FLOOR + PCB_POST_HEIGHT, omit_bottom=True)

    write_stl(tris)
    print(f"wrote {OUT} ({OUTER_LENGTH:.1f} x {OUTER_WIDTH:.1f} x {OUTER_HEIGHT:.1f} mm)")


if __name__ == "__main__":
    main()
