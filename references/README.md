# References

Third-party implementations of Luminet's 1979 black hole visualization that
informed the eventHorizon codebase. These are **read-only** — the actual
running code is in `eventHorizon/`.

## luminet/

Python implementation by [@rmusic](https://github.com/rmusic/luminet).
Source of the elliptic integral impact parameter solver, Novikov-Thorne flux,
and redshift formulas that eventHorizon's physics is based on.

- `paper/` — Luminet's original 1979 paper (PDF)
- `code/` — Core Python modules (bh_math, black_hole, isoradials, isoredshift)
- `validation/` — Pre-computed CSV point data at various inclinations,
  used for regression testing against eventHorizon output

## bhsim/

Python implementation by [@rmusic](https://github.com/rmusic/bhsim).
Alternative approach with different rendering pipeline. Used as a
cross-reference during development.

- `code/` — Core Python modules (blackhole, data, util, out, benchmark)
