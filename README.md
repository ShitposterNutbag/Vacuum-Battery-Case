# Vacuum Battery Case

## Project Goal

Design a custom 3D printable enclosure for a salvaged cordless vacuum battery pack.

The enclosure will:
- Hold the existing battery pack securely.
- Expose the USB-C charging port.
- Expose the power button.
- Allow the charge indicator LEDs to remain visible.
- Be printable on an FDM printer.
- Be easy to assemble and modify.

---

# Repository Structure

cad/
- Generated CAD files
- STEP files
- STL files
- Future design revisions

scans/
- RealityScan reference meshes
- OBJ
- STL
- GLB
- MTL
- Texture images

reference/
- Photos
- Measurements
- Notes
- Design references

---

# Current Status

RealityScan mesh has been captured.

Known artifacts include:
- Piece of tabletop attached to the bottom.
- Piece of tape protruding from one side.
- Minor photogrammetry surface noise.

These artifacts should be removed before enclosure design begins.

---

# Design Philosophy

The scan is NOT the final model.

The scan is used ONLY as a dimensional reference.

The final enclosure should be a clean, fully parametric CAD model.

Do not reproduce scan imperfections.

Maintain reasonable clearances around the battery pack for easy installation.

---

# Development Workflow

Phase 1
- Clean the scan.
- Remove artifacts.
- Preserve battery geometry.

Phase 2
- Create a simplified reference model.

Phase 3
- Design the enclosure.

Phase 4
- Test fit.
- Revise.
- Optimize.

---

# Current Files

Primary reference files:

- scans/6_30_2026.obj
- scans/6_30_2026.stl
- scans/6_30_2026.glb
- scans/6_30_2026.mtl

---

# Design Requirements

The finished enclosure should:

- Fit the scanned battery pack.
- Include adequate internal clearance.
- Provide openings for:
  - USB-C charging port
  - Power button
  - LED indicators
- Be printable without excessive supports whenever practical.
- Be durable while minimizing unnecessary material.

---

# Long-Term Goal

Develop a reusable workflow using RealityScan, GitHub, AI-assisted CAD generation, and 3D printing for designing custom enclosures around salvaged electronics.

This repository is intended to become the foundation for future custom battery packs, electronics enclosures, and similar reverse-engineering projects.
