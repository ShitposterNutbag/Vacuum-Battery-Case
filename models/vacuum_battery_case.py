"""Parametric CadQuery fit-check enclosure for the vacuum battery/BMS assembly.

Coordinate system (mm):
- X: battery length, left to right.
- Y: battery width, front to back.
- Z: height, bottom to lid.
- The battery cavity origin is the inside lower-left-front corner.

The scan/photos were unavailable in the repo at generation time. External feature
cutouts are intentionally disabled until measured coordinates are entered below.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Literal

import cadquery as cq

Side = Literal["front", "back", "left", "right"]


@dataclass
class RectCutout:
    name: str
    side: Side
    center_x: float
    center_y: float
    center_z: float
    width: float
    height: float
    enabled: bool = False


@dataclass
class RoundCutout:
    name: str
    side: Side
    center_x: float
    center_y: float
    center_z: float
    diameter: float
    enabled: bool = False


@dataclass
class Params:
    battery_len: float = 100.0
    battery_width: float = 69.3
    battery_height: float = 40.0
    clearance: float = 0.5
    wall: float = 2.0
    floor: float = 2.0
    lid_thickness: float = 3.0
    lid_overlap: float = 4.0
    corner_radius: float = 4.0
    rib_width: float = 3.0
    rib_height: float = 8.0
    rib_clearance: float = 0.2
    magnet_diameter: float = 10.0
    magnet_depth: float = 3.0
    wire_channel_width: float = 8.0
    wire_channel_depth: float = 1.2
    rect_cutouts: list[RectCutout] = field(default_factory=list)
    round_cutouts: list[RoundCutout] = field(default_factory=list)

    @property
    def cavity_len(self) -> float:
        return self.battery_len + 2 * self.clearance

    @property
    def cavity_width(self) -> float:
        return self.battery_width + 2 * self.clearance

    @property
    def cavity_height(self) -> float:
        return self.battery_height + self.clearance

    @property
    def outer_len(self) -> float:
        return self.cavity_len + 2 * self.wall

    @property
    def outer_width(self) -> float:
        return self.cavity_width + 2 * self.wall

    @property
    def base_height(self) -> float:
        return self.floor + self.cavity_height


def _shell_box(p: Params) -> cq.Workplane:
    outer = (
        cq.Workplane("XY")
        .box(p.outer_len, p.outer_width, p.base_height, centered=(False, False, False))
        .edges("|Z")
        .fillet(p.corner_radius)
    )
    cavity = cq.Workplane("XY").box(
        p.cavity_len, p.cavity_width, p.cavity_height + 0.2, centered=(False, False, False)
    ).translate((p.wall, p.wall, p.floor))
    return outer.cut(cavity)


def _add_ribs_and_wire_channels(base: cq.Workplane, p: Params) -> cq.Workplane:
    # Low ribs locate the pack without clamping it; ribs are below the BMS/ports.
    rib_z = p.floor
    x_positions = [p.wall + 18, p.wall + p.cavity_len - 18]
    for x in x_positions:
        base = base.union(
            cq.Workplane("XY")
            .box(p.rib_width, p.cavity_width - 16, p.rib_height, centered=(False, False, False))
            .translate((x, p.wall + 8, rib_z))
        )
    y_positions = [p.wall + 10, p.wall + p.cavity_width - 10 - p.rib_width]
    for y in y_positions:
        base = base.union(
            cq.Workplane("XY")
            .box(p.cavity_len - 24, p.rib_width, p.rib_height, centered=(False, False, False))
            .translate((p.wall + 12, y, rib_z))
        )
    # Shallow floor wire channels, one longitudinal and one transverse.
    ch1 = cq.Workplane("XY").box(
        p.cavity_len - 20, p.wire_channel_width, p.wire_channel_depth, centered=(False, False, False)
    ).translate((p.wall + 10, p.wall + p.cavity_width / 2 - p.wire_channel_width / 2, p.floor - p.wire_channel_depth))
    ch2 = cq.Workplane("XY").box(
        p.wire_channel_width, p.cavity_width - 20, p.wire_channel_depth, centered=(False, False, False)
    ).translate((p.wall + p.cavity_len / 2 - p.wire_channel_width / 2, p.wall + 10, p.floor - p.wire_channel_depth))
    return base.cut(ch1).cut(ch2)


def _side_cut_box(p: Params, cut: RectCutout) -> cq.Workplane:
    x = p.wall + cut.center_x
    y = p.wall + cut.center_y
    z = p.floor + cut.center_z
    depth = p.wall + 0.6
    if cut.side == "front":
        return cq.Workplane("XY").box(cut.width, depth, cut.height).translate((x, p.wall / 2, z))
    if cut.side == "back":
        return cq.Workplane("XY").box(cut.width, depth, cut.height).translate((x, p.wall + p.cavity_width + p.wall / 2, z))
    if cut.side == "left":
        return cq.Workplane("XY").box(depth, cut.width, cut.height).translate((p.wall / 2, y, z))
    return cq.Workplane("XY").box(depth, cut.width, cut.height).translate((p.wall + p.cavity_len + p.wall / 2, y, z))


def _side_cut_cylinder(p: Params, cut: RoundCutout) -> cq.Workplane:
    x = p.wall + cut.center_x
    y = p.wall + cut.center_y
    z = p.floor + cut.center_z
    depth = p.wall + 0.8
    if cut.side in ("front", "back"):
        loc_y = p.wall / 2 if cut.side == "front" else p.wall + p.cavity_width + p.wall / 2
        return cq.Workplane("XZ").circle(cut.diameter / 2).extrude(depth).translate((x, loc_y - depth / 2, z))
    loc_x = p.wall / 2 if cut.side == "left" else p.wall + p.cavity_len + p.wall / 2
    return cq.Workplane("YZ").circle(cut.diameter / 2).extrude(depth).translate((loc_x - depth / 2, y, z))


def _apply_feature_cutouts(base: cq.Workplane, p: Params) -> cq.Workplane:
    for cut in p.rect_cutouts:
        if cut.enabled:
            base = base.cut(_side_cut_box(p, cut))
    for cut in p.round_cutouts:
        if cut.enabled:
            base = base.cut(_side_cut_cylinder(p, cut))
    return base


def _cut_magnets(part: cq.Workplane, p: Params, z_top: float, from_top: bool = True) -> cq.Workplane:
    inset = p.wall + p.magnet_diameter / 2 + 3
    pts = [(inset, inset), (p.outer_len - inset, inset), (inset, p.outer_width - inset), (p.outer_len - inset, p.outer_width - inset)]
    z = z_top - p.magnet_depth if from_top else z_top
    for x, y in pts:
        pocket = cq.Workplane("XY").circle(p.magnet_diameter / 2).extrude(p.magnet_depth).translate((x, y, z))
        part = part.cut(pocket)
    return part


def make_base(p: Params = Params()) -> cq.Workplane:
    base = _shell_box(p)
    base = _add_ribs_and_wire_channels(base, p)
    base = _cut_magnets(base, p, p.base_height)
    base = _apply_feature_cutouts(base, p)
    return base


def make_lid(p: Params = Params()) -> cq.Workplane:
    lid = cq.Workplane("XY").box(p.outer_len, p.outer_width, p.lid_thickness, centered=(False, False, False)).edges("|Z").fillet(p.corner_radius)
    lip = cq.Workplane("XY").box(
        p.cavity_len - 0.4, p.cavity_width - 0.4, p.lid_overlap, centered=(False, False, False)
    ).translate((p.wall + 0.2, p.wall + 0.2, -p.lid_overlap))
    lid = lid.union(lip)
    lid = _cut_magnets(lid, p, p.lid_thickness)
    return lid


def params_from_json(path: str | Path) -> Params:
    """Load measured cutout parameters from JSON without making assumptions."""
    data: dict[str, Any] = json.loads(Path(path).read_text())
    p = Params(**{k: v for k, v in data.items() if k not in {"rect_cutouts", "round_cutouts"}})
    p.rect_cutouts = [RectCutout(**item) for item in data.get("rect_cutouts", [])]
    p.round_cutouts = [RoundCutout(**item) for item in data.get("round_cutouts", [])]
    return p


def export_all(out_dir: str | Path = "exports", params: Params | None = None) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    p = params or Params()
    base = make_base(p)
    lid = make_lid(p)
    cq.exporters.export(base, str(out / "vacuum_battery_case_base.step"))
    cq.exporters.export(lid, str(out / "vacuum_battery_case_lid.step"))
    cq.exporters.export(base, str(out / "vacuum_battery_case_base.stl"))
    cq.exporters.export(lid, str(out / "vacuum_battery_case_lid.stl"))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export the vacuum battery case fit-check model.")
    parser.add_argument("--params", help="Optional JSON file containing measured cutout parameters.")
    parser.add_argument("--out", default="exports", help="Output directory for STEP/STL files.")
    args = parser.parse_args()
    export_all(args.out, params_from_json(args.params) if args.params else None)
