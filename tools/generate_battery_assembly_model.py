#!/usr/bin/env python3
"""Generate measured battery assembly review CAD as STL and STEP.

This generator intentionally ignores inferred cell placement from the cleaned
scan.  The six-cell pack is built from measured dimensions supplied by the user:
18.0 mm diameter, 68.9 mm cell length, 2 columns by 3 rows, tangent cells.
The cleaned scan remains the reference for non-cell context: holder/end-cap
presence and approximate relative PCB/component side placement.

No enclosure, tray, or shell geometry is generated.
"""
from __future__ import annotations

import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN = ROOT / "6_30_2026v2.glb"
STL_OUT = ROOT / "output" / "vacuum_battery_assembly_model.stl"
STEP_OUT = ROOT / "output" / "vacuum_battery_assembly_model.step"
MANIFEST = ROOT / "output" / "vacuum_battery_assembly_model.json"

SCALE_MM_PER_SCAN_UNIT = 50.0
CELL_DIAMETER = 18.0
CELL_RADIUS = CELL_DIAMETER / 2
CELL_LENGTH = 68.9
CELL_SEGMENTS = 40
CELL_COLUMNS = 2
CELL_ROWS = 3
PCB_OFFSET_FROM_BATTERY = 2.0
BOARD_THICKNESS = 1.6
HOLDER_CAP_THICKNESS = 2.4
HOLDER_RAIL_THICKNESS = 2.0
HOLDER_RAIL_WIDTH = 4.0
WIRE_DIAMETER = 2.0

# Component dimensions/locations are placed relative to the measured cell pack
# and PCB faces; these are the features requiring dimensional review before tray work.
LONG_PCB = dict(width=48.0, height=66.0)
SHORT_PCB = dict(width=36.0, height=42.0)
DC_JACK = dict(x=-12.0, z=37.0, diameter=9.5, length=12.0)
POWER_SWITCH = dict(x=12.0, z=20.0, width=12.0, height=7.0, protrusion=3.2)
LONG_CONNECTOR = dict(x=-14.0, z=-16.0, width=9.0, height=8.0, protrusion=3.0)
SHORT_CONNECTOR = dict(x=11.0, z=-14.0, width=9.0, height=7.0, protrusion=2.5)
LED_POSITIONS = [(-12.0, 12.0), (-4.0, 12.0), (4.0, 12.0), (12.0, 12.0)]
VACUUM_BUTTON = dict(x=0.0, z=0.0, width=7.0, height=5.0, protrusion=1.5)


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


def add_cylinder_y(tris, cx, cy, cz, length, radius, segments=CELL_SEGMENTS):
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
    x0, y0, z0 = start
    x1, y1, z1 = end
    add_box(
        tris,
        (x0 + x1) / 2,
        (y0 + y1) / 2,
        (z0 + z1) / 2,
        max(abs(x1 - x0), diameter),
        max(abs(y1 - y0), diameter),
        max(abs(z1 - z0), diameter),
    )


def measured_pack_dimensions():
    return (CELL_COLUMNS * CELL_DIAMETER, CELL_LENGTH, CELL_ROWS * CELL_DIAMETER)


def add_cells(tris):
    for row in range(CELL_ROWS):
        for col in range(CELL_COLUMNS):
            x = (col - (CELL_COLUMNS - 1) / 2) * CELL_DIAMETER
            z = (row - (CELL_ROWS - 1) / 2) * CELL_DIAMETER
            add_cylinder_y(tris, x, 0, z, CELL_LENGTH, CELL_RADIUS)


def add_scan_retained_holders(tris, pack_w, pack_d, pack_h):
    # End caps and rails retain the scan-observed holder/end-cap concept but are
    # sized around the measured tangent cell pack.
    cap_w = pack_w + 5.0
    cap_h = pack_h + 5.0
    for y in (-(pack_d / 2 + HOLDER_CAP_THICKNESS / 2), pack_d / 2 + HOLDER_CAP_THICKNESS / 2):
        add_box(tris, 0, y, 0, cap_w, HOLDER_CAP_THICKNESS, cap_h)
    for x in (-(pack_w / 2 + HOLDER_RAIL_THICKNESS / 2), pack_w / 2 + HOLDER_RAIL_THICKNESS / 2):
        add_box(tris, x, 0, 0, HOLDER_RAIL_THICKNESS, pack_d + 2 * HOLDER_CAP_THICKNESS, pack_h + 4.0)
    for z in (-(pack_h / 2 + HOLDER_RAIL_THICKNESS / 2), pack_h / 2 + HOLDER_RAIL_THICKNESS / 2):
        add_box(tris, 0, 0, z, pack_w + 4.0, pack_d + 2 * HOLDER_CAP_THICKNESS, HOLDER_RAIL_WIDTH)


def add_pcbs_and_features(tris, pack_d):
    front_surface = -(pack_d / 2)
    back_surface = pack_d / 2
    long_y = front_surface - PCB_OFFSET_FROM_BATTERY - BOARD_THICKNESS / 2
    short_y = back_surface + PCB_OFFSET_FROM_BATTERY + BOARD_THICKNESS / 2

    add_box(tris, 0, long_y, 0, LONG_PCB["width"], BOARD_THICKNESS, LONG_PCB["height"])
    add_cylinder_y(tris, DC_JACK["x"], long_y - (BOARD_THICKNESS + DC_JACK["length"]) / 2, DC_JACK["z"], DC_JACK["length"], DC_JACK["diameter"] / 2, segments=32)
    add_box(tris, POWER_SWITCH["x"], long_y - BOARD_THICKNESS / 2 - POWER_SWITCH["protrusion"] / 2, POWER_SWITCH["z"], POWER_SWITCH["width"], POWER_SWITCH["protrusion"], POWER_SWITCH["height"])
    add_box(tris, LONG_CONNECTOR["x"], long_y - BOARD_THICKNESS / 2 - LONG_CONNECTOR["protrusion"] / 2, LONG_CONNECTOR["z"], LONG_CONNECTOR["width"], LONG_CONNECTOR["protrusion"], LONG_CONNECTOR["height"])

    add_box(tris, 0, short_y, 0, SHORT_PCB["width"], BOARD_THICKNESS, SHORT_PCB["height"])
    for x, z in LED_POSITIONS:
        add_cylinder_y(tris, x, short_y + BOARD_THICKNESS / 2 + 1.0, z, 2.0, 1.7, segments=16)
    add_box(tris, VACUUM_BUTTON["x"], short_y + BOARD_THICKNESS / 2 + VACUUM_BUTTON["protrusion"] / 2, VACUUM_BUTTON["z"], VACUUM_BUTTON["width"], VACUUM_BUTTON["protrusion"], VACUUM_BUTTON["height"])
    add_box(tris, SHORT_CONNECTOR["x"], short_y + BOARD_THICKNESS / 2 + SHORT_CONNECTOR["protrusion"] / 2, SHORT_CONNECTOR["z"], SHORT_CONNECTOR["width"], SHORT_CONNECTOR["protrusion"], SHORT_CONNECTOR["height"])

    add_wire_segment(tris, (LONG_CONNECTOR["x"], long_y - 2.0, LONG_CONNECTOR["z"]), (-8, -10, -12))
    add_wire_segment(tris, (-8, -10, -12), (-8, -3, 10))
    add_wire_segment(tris, (SHORT_CONNECTOR["x"], short_y + 2.0, SHORT_CONNECTOR["z"]), (8, 10, -10))
    add_wire_segment(tris, (8, 10, -10), (8, 3, 12))

    return long_y, short_y


def make_model():
    scan_min, scan_max = scan_bbox(SCAN)
    scan_dims = tuple((scan_max[i] - scan_min[i]) * SCALE_MM_PER_SCAN_UNIT for i in range(3))
    pack_w, pack_d, pack_h = measured_pack_dimensions()
    tris = []
    add_cells(tris)
    add_scan_retained_holders(tris, pack_w, pack_d, pack_h)
    long_y, short_y = add_pcbs_and_features(tris, pack_d)
    return tris, scan_dims, (pack_w, pack_d, pack_h), (long_y, short_y)


def normal(a, b, c):
    ux, uy, uz = [b[i] - a[i] for i in range(3)]
    vx, vy, vz = [c[i] - a[i] for i in range(3)]
    n = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
    length = math.sqrt(sum(i * i for i in n)) or 1.0
    return tuple(i / length for i in n)


def write_stl(tris, path: Path):
    with path.open("w") as f:
        f.write("solid vacuum_battery_assembly_model\n")
        for a, b, c in tris:
            n = normal(a, b, c)
            f.write(f" facet normal {n[0]:.6g} {n[1]:.6g} {n[2]:.6g}\n  outer loop\n")
            for p in (a, b, c):
                f.write(f"   vertex {p[0]:.6g} {p[1]:.6g} {p[2]:.6g}\n")
            f.write("  endloop\n endfacet\n")
        f.write("endsolid vacuum_battery_assembly_model\n")


def step_coord(p):
    return f"({p[0]:.6f},{p[1]:.6f},{p[2]:.6f})"


def write_step(tris, path: Path):
    # Minimal AP214 faceted BREP.  The STEP is intentionally derived from the same
    # triangulated review geometry as the STL so both formats verify identical dimensions.
    entities: list[str] = []

    def add(entity: str) -> int:
        entities.append(entity)
        return len(entities)

    origin = add("CARTESIAN_POINT('',(0.,0.,0.))")
    z_dir = add("DIRECTION('',(0.,0.,1.))")
    x_dir = add("DIRECTION('',(1.,0.,0.))")
    placement = add(f"AXIS2_PLACEMENT_3D('',#{origin},#{z_dir},#{x_dir})")
    geom_context = add(f"GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{add('UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#' + str(add("(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.))")) + ",'distance_accuracy_value','confusion accuracy')")})) GLOBAL_UNIT_ASSIGNED_CONTEXT((#{entities.index('(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.))')+1})) REPRESENTATION_CONTEXT('','3D')")
    faces = []
    for a, b, c in tris:
        n = normal(a, b, c)
        ref = (1.0, 0.0, 0.0) if abs(n[0]) < 0.9 else (0.0, 1.0, 0.0)
        pids = [add(f"CARTESIAN_POINT('',{step_coord(p)})") for p in (a, b, c)]
        vids = [add(f"VERTEX_POINT('',#{pid})") for pid in pids]
        loop = add(f"POLY_LOOP('',(#{vids[0]},#{vids[1]},#{vids[2]}))")
        bound = add(f"FACE_OUTER_BOUND('',#{loop},.T.)")
        face_origin = add(f"CARTESIAN_POINT('',{step_coord(a)})")
        face_normal = add(f"DIRECTION('',({n[0]:.8f},{n[1]:.8f},{n[2]:.8f}))")
        face_ref = add(f"DIRECTION('',({ref[0]:.8f},{ref[1]:.8f},{ref[2]:.8f}))")
        face_place = add(f"AXIS2_PLACEMENT_3D('',#{face_origin},#{face_normal},#{face_ref})")
        plane = add(f"PLANE('',#{face_place})")
        faces.append(add(f"ADVANCED_FACE('',(#{bound}),#{plane},.T.)"))
    shell = add("CLOSED_SHELL('',(" + ",".join(f"#{f}" for f in faces) + "))")
    brep = add(f"MANIFOLD_SOLID_BREP('vacuum_battery_assembly_model',#{shell})")
    shape = add(f"SHAPE_REPRESENTATION('vacuum_battery_assembly_model',(#{placement},#{brep}),#{geom_context})")
    product = add("PRODUCT('vacuum_battery_assembly_model','vacuum_battery_assembly_model','',(#" + str(add("PRODUCT_CONTEXT('',#" + str(add("APPLICATION_CONTEXT('automotive_design')")) + ",'mechanical')")) + "))")
    add("PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE('','',#" + str(product) + ",.MADE.)")
    add(f"SHAPE_DEFINITION_REPRESENTATION(#{len(entities)},#{shape})")

    with path.open("w") as f:
        f.write("ISO-10303-21;\nHEADER;\n")
        f.write("FILE_DESCRIPTION(('Battery assembly dimensional review model'),'2;1');\n")
        f.write("FILE_NAME('vacuum_battery_assembly_model.step','2026-07-01T00:00:00',('OpenAI'),('OpenAI'),'','','');\n")
        f.write("FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\nENDSEC;\nDATA;\n")
        for i, entity in enumerate(entities, 1):
            f.write(f"#{i}={entity};\n")
        f.write("ENDSEC;\nEND-ISO-10303-21;\n")


def write_manifest(scan_dims, pack_dims, pcb_y):
    manifest = {
        "source_scan": str(SCAN.relative_to(ROOT)),
        "scale_mm_per_scan_unit": SCALE_MM_PER_SCAN_UNIT,
        "scan_bbox_mm": {"x": round(scan_dims[0], 3), "y": round(scan_dims[1], 3), "z": round(scan_dims[2], 3)},
        "cell_specification": {
            "type": "18650",
            "diameter_mm": CELL_DIAMETER,
            "length_mm": CELL_LENGTH,
            "arrangement": "2 columns x 3 rows",
            "intentional_gap_mm": 0.0,
            "pack_width_mm": pack_dims[0],
            "pack_depth_mm": pack_dims[1],
            "pack_height_mm": pack_dims[2],
        },
        "pcb_offsets": {
            "offset_from_battery_surface_mm": PCB_OFFSET_FROM_BATTERY,
            "long_pcb_y_center_mm": round(pcb_y[0], 3),
            "short_pcb_y_center_mm": round(pcb_y[1], 3),
        },
        "modeled_components": [
            "six tangent measured 18650 cells",
            "scan-retained battery holder end caps and rails",
            "long PCB with DC barrel jack, power switch, connector, and wiring",
            "short PCB with LED/button circuitry, connector, and wiring",
        ],
        "no_enclosure_or_tray_generated": True,
        "outputs": [str(STL_OUT.relative_to(ROOT)), str(STEP_OUT.relative_to(ROOT))],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")


def main():
    tris, scan_dims, pack_dims, pcb_y = make_model()
    STL_OUT.parent.mkdir(exist_ok=True)
    write_stl(tris, STL_OUT)
    write_step(tris, STEP_OUT)
    write_manifest(scan_dims, pack_dims, pcb_y)
    print(
        f"wrote {STL_OUT}, {STEP_OUT}, and {MANIFEST}; facets={len(tris)}; "
        f"measured pack {pack_dims[0]:.1f} W x {pack_dims[1]:.1f} D x {pack_dims[2]:.1f} H mm"
    )


if __name__ == "__main__":
    main()
