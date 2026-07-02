# Vacuum Battery Case

Parametric CadQuery project for a 3D-printable enclosure framework for an existing vacuum battery pack.

This first commit intentionally does **not** try to fit the actual electronics.  It provides a clean, configurable enclosure scaffold that can be refined after the battery pack, charging board, connector, LED, button, and wiring dimensions are measured.

## Project layout

```text
/
├── README.md
├── requirements.txt
├── config.py
├── enclosure.py
├── export.py
└── generated/
```

## Requirements

- Python 3.10 or newer
- CadQuery 2.x
- All dimensions are in millimeters

## Install

Create a virtual environment and install the CadQuery dependency:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> CadQuery ships compiled dependencies. If installation fails on your platform, use the CadQuery project installation guidance for your operating system or install CadQuery in a Conda environment.

## Generate CAD exports

Run:

```bash
python export.py
```

The script writes generated files to `generated/`:

- `generated/base.stl`
- `generated/lid.stl`
- `generated/base.step` when STEP export is available
- `generated/lid.step` when STEP export is available

## Parametric configuration

Edit `config.py` to change the model.  All dimensions and feature placeholders are defined there, including:

- 2.0 mm wall thickness
- 0.5 mm default component clearance
- Overall enclosure length, width, base height, lid height, and corner radius
- Magnet pocket diameter and depth
- Battery pack planning placeholder
- USB charging board placeholder
- DC barrel jack placeholder
- LED window placeholders
- Push button placeholder
- Wire routing channel placeholder

## Design notes

- `enclosure.py` contains `make_base()` and `make_lid()` CadQuery model builders.
- `export.py` exports STL files and STEP files when supported by the local CadQuery installation.
- The lid is designed for magnet retention using four configurable 10.0 mm diameter by 3.0 mm deep magnet pockets.
- Placeholder geometry is intentionally easy to find and revise later; it is not a final electronics fit.
