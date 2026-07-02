#!/usr/bin/env python3
"""Clean the RealityScan battery mesh for CAD-reference use.

The script removes only the known scan artifacts documented in README.md and
SCAN_NOTES.md: the low tabletop/support surface, the thin side protrusion, and
tiny floating fragments. It then caps cleanup-created boundary loops and exports
watertight OBJ and binary STL files.

Default input is scans/6_30_2026.obj. If that file is not present in the working
copy, the script reads 6_30_2026.obj directly from scans/Mesh 7_2.zip, which is
the archived RealityScan OBJ bundle in this repository.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import math
import struct
import zipfile


DEFAULT_INPUT = Path("scans/6_30_2026.obj")
DEFAULT_ZIP_FALLBACK = Path("scans/Mesh 7_2.zip")
DEFAULT_ZIP_MEMBER = "6_30_2026.obj"
DEFAULT_OBJ_OUTPUT = Path("scans/cleaned/cleaned_battery.obj")
DEFAULT_STL_OUTPUT = Path("scans/cleaned/cleaned_battery.stl")

# Conservative artifact thresholds from the captured mesh coordinate space.
TABLETOP_Y_MAX = 0.060
SIDE_PROTRUSION_X_MIN = -0.180
MIN_FLOATING_COMPONENT_FACES = 4


@dataclass(frozen=True)
class Mesh:
    vertices: list[tuple[float, float, float]]
    faces: list[tuple[int, int, int]]


def read_obj_text(path: Path, zip_fallback: Path, zip_member: str) -> str:
    if path.exists():
        return path.read_text()
    if zip_fallback.exists():
        with zipfile.ZipFile(zip_fallback) as archive:
            return archive.read(zip_member).decode("utf-8")
    raise FileNotFoundError(
        f"Could not find {path} or fallback archive member {zip_member!r} in {zip_fallback}"
    )


def parse_obj(text: str) -> Mesh:
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []

    for line in text.splitlines():
        if line.startswith("v "):
            _, x, y, z, *_ = line.split()
            vertices.append((float(x), float(y), float(z)))
        elif line.startswith("f "):
            face = [int(part.split("/")[0]) - 1 for part in line.split()[1:]]
            if len(face) == 3:
                faces.append((face[0], face[1], face[2]))
            elif len(face) > 3:
                for idx in range(1, len(face) - 1):
                    faces.append((face[0], face[idx], face[idx + 1]))

    return Mesh(vertices, faces)


def removes_known_artifact(face: tuple[int, int, int], vertices: list[tuple[float, float, float]]) -> bool:
    points = [vertices[index] for index in face]

    # Remove the low, flat tabletop/support material captured under the battery.
    if min(point[1] for point in points) < TABLETOP_Y_MAX:
        return True

    # Remove the far-left thin protrusion documented as tape/scan artifact.
    if min(point[0] for point in points) < SIDE_PROTRUSION_X_MIN:
        return True

    return False


def remove_tiny_floating_components(faces: list[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
    edge_to_faces: dict[tuple[int, int], list[int]] = defaultdict(list)
    for face_index, face in enumerate(faces):
        for a, b in face_edges(face):
            edge_to_faces[tuple(sorted((a, b)))].append(face_index)

    adjacency = [set() for _ in faces]
    for connected_faces in edge_to_faces.values():
        for a in connected_faces:
            adjacency[a].update(face for face in connected_faces if face != a)

    seen = [False] * len(faces)
    kept_face_indices: set[int] = set()

    for start in range(len(faces)):
        if seen[start]:
            continue
        stack = [start]
        seen[start] = True
        component: list[int] = []

        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in adjacency[current]:
                if not seen[neighbor]:
                    seen[neighbor] = True
                    stack.append(neighbor)

        if len(component) >= MIN_FLOATING_COMPONENT_FACES:
            kept_face_indices.update(component)

    return [face for index, face in enumerate(faces) if index in kept_face_indices]


def reindex_mesh(vertices: list[tuple[float, float, float]], faces: list[tuple[int, int, int]]) -> Mesh:
    used_vertices = sorted({vertex for face in faces for vertex in face})
    remap = {old_index: new_index for new_index, old_index in enumerate(used_vertices)}
    return Mesh(
        [vertices[index] for index in used_vertices],
        [tuple(remap[index] for index in face) for face in faces],
    )


def face_edges(face: tuple[int, int, int]) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    return ((face[0], face[1]), (face[1], face[2]), (face[2], face[0]))


def boundary_loops(faces: list[tuple[int, int, int]]) -> list[list[int]]:
    edge_counts: dict[tuple[int, int], int] = defaultdict(int)
    for face in faces:
        for a, b in face_edges(face):
            edge_counts[tuple(sorted((a, b)))] += 1

    boundary_edges = [edge for edge, count in edge_counts.items() if count == 1]
    boundary_adjacency: dict[int, list[int]] = defaultdict(list)
    for a, b in boundary_edges:
        boundary_adjacency[a].append(b)
        boundary_adjacency[b].append(a)

    unused = set(boundary_edges)
    loops: list[list[int]] = []

    while unused:
        a, b = next(iter(unused))
        loop = [a, b]
        unused.remove(tuple(sorted((a, b))))
        previous, current = a, b

        while True:
            next_vertices = [
                candidate
                for candidate in boundary_adjacency[current]
                if candidate != previous and tuple(sorted((current, candidate))) in unused
            ]
            if not next_vertices:
                break

            next_vertex = next_vertices[0]
            unused.remove(tuple(sorted((current, next_vertex))))
            if next_vertex == loop[0]:
                break

            loop.append(next_vertex)
            previous, current = current, next_vertex

        if len(loop) >= 3:
            loops.append(loop)

    return loops


def cap_boundary_loops(mesh: Mesh) -> Mesh:
    vertices = list(mesh.vertices)
    faces = list(mesh.faces)

    for loop in boundary_loops(faces):
        centroid = tuple(sum(vertices[index][axis] for index in loop) / len(loop) for axis in range(3))
        centroid_index = len(vertices)
        vertices.append(centroid)  # type: ignore[arg-type]

        for index, vertex in enumerate(loop):
            faces.append((vertex, loop[(index + 1) % len(loop)], centroid_index))

    return Mesh(vertices, faces)


def clean_mesh(mesh: Mesh) -> Mesh:
    faces = [face for face in mesh.faces if not removes_known_artifact(face, mesh.vertices)]
    faces = remove_tiny_floating_components(faces)
    return cap_boundary_loops(reindex_mesh(mesh.vertices, faces))


def normal(a: tuple[float, float, float], b: tuple[float, float, float], c: tuple[float, float, float]) -> tuple[float, float, float]:
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    length = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return nx / length, ny / length, nz / length


def write_obj(mesh: Mesh, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as output:
        output.write("# Cleaned RealityScan battery reference mesh\n")
        for vertex in mesh.vertices:
            output.write("v %.9f %.9f %.9f\n" % vertex)
        for face in mesh.faces:
            output.write("f %d %d %d\n" % (face[0] + 1, face[1] + 1, face[2] + 1))


def write_binary_stl(mesh: Mesh, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as output:
        output.write(b"Cleaned RealityScan battery reference mesh".ljust(80, b" "))
        output.write(struct.pack("<I", len(mesh.faces)))
        for face in mesh.faces:
            triangle = [mesh.vertices[index] for index in face]
            output.write(struct.pack("<12fH", *(normal(*triangle) + triangle[0] + triangle[1] + triangle[2] + (0,))))


def mesh_edge_validation(mesh: Mesh) -> tuple[int, int]:
    edge_counts: dict[tuple[int, int], int] = defaultdict(int)
    for face in mesh.faces:
        for a, b in face_edges(face):
            edge_counts[tuple(sorted((a, b)))] += 1
    nonmanifold_edges = sum(1 for count in edge_counts.values() if count != 2)
    boundary_edges = sum(1 for count in edge_counts.values() if count == 1)
    return nonmanifold_edges, boundary_edges


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--zip-fallback", type=Path, default=DEFAULT_ZIP_FALLBACK)
    parser.add_argument("--zip-member", default=DEFAULT_ZIP_MEMBER)
    parser.add_argument("--obj-output", type=Path, default=DEFAULT_OBJ_OUTPUT)
    parser.add_argument("--stl-output", type=Path, default=DEFAULT_STL_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_text = read_obj_text(args.input, args.zip_fallback, args.zip_member)
    source_mesh = parse_obj(source_text)
    cleaned_mesh = clean_mesh(source_mesh)
    write_obj(cleaned_mesh, args.obj_output)
    write_binary_stl(cleaned_mesh, args.stl_output)

    nonmanifold_edges, boundary_edges = mesh_edge_validation(cleaned_mesh)
    print(f"obj_output={args.obj_output}")
    print(f"stl_output={args.stl_output}")
    print(f"source_vertices={len(source_mesh.vertices)} source_faces={len(source_mesh.faces)}")
    print(f"cleaned_vertices={len(cleaned_mesh.vertices)} cleaned_faces={len(cleaned_mesh.faces)}")
    print(f"nonmanifold_edges={nonmanifold_edges} boundary_edges={boundary_edges}")

    if nonmanifold_edges or boundary_edges:
        raise SystemExit("Cleaned mesh validation failed")


if __name__ == "__main__":
    main()
