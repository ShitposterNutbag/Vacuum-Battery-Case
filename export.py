"""Export the parametric CadQuery enclosure models."""

from __future__ import annotations

from pathlib import Path

import cadquery as cq
from cadquery import exporters

import config as cfg
from enclosure import make_base, make_lid


def _export_part(part: cq.Workplane, name: str, output_dir: Path) -> None:
    """Export one part using the configured file formats."""
    if cfg.EXPORT_STL:
        exporters.export(
            part,
            str(output_dir / f"{name}.stl"),
            tolerance=cfg.STL_TOLERANCE,
            angularTolerance=cfg.STL_ANGULAR_TOLERANCE,
        )

    if cfg.EXPORT_STEP:
        exporters.export(part, str(output_dir / f"{name}.step"))


def main() -> None:
    """Generate all configured enclosure exports."""
    output_dir = Path(cfg.GENERATED_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    _export_part(make_base(), "base", output_dir)
    _export_part(make_lid(), "lid", output_dir)


if __name__ == "__main__":
    main()
