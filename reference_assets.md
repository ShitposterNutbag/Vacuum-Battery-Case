# Reference asset retrieval status

I attempted to retrieve the committed reference assets requested by the user:

- `6_30_2026.glb`
- reference photo ZIP containing 8 grid-paper photos

The local checkout has no configured Git remote and no `main` branch/reference is present, so there is no repository URL available from this environment to fetch those assets. A filesystem search under `/workspace` and `/` also found no copy of `6_30_2026.glb` or any reference-photo ZIP.

Because the scan/photos are unavailable here, no scan-derived or photo-derived feature positions have been used. The CadQuery model remains measurement-driven and must not be treated as final until the measurements listed in `docs/missing_measurements.md` are filled from the scan/photos or direct caliper measurements.
