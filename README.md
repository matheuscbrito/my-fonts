# Senna Display

A personal display serif for headlines, defined entirely in code. The feel
(high contrast, sharp bracketed wedge serifs, large x-height, tight spacing) is
inspired by the headline faces on sites like tako.ai, but every outline here
is original.

## Layout

- `font/params.py`: the shared design settings (metrics, stem weights, serif shape, spacing). Start here.
- `font/draw.py`: drawing primitives (contours, ellipses, boolean union/cut).
- `font/parts.py`: reusable letter parts (serifs, arches, bowls, pen-angle bars and cuts, the broad-nib `nib_stroke`).
- `font/glyphs.py`: one function per glyph.
- `font/kerning.py`: kerning groups and values, written to the `kern` feature at build time.
- `build.py`: draws every glyph and writes `dist/*.otf` and `dist/*.woff2`.
- `specimen/index.html`: specimen page. `specimen/proof.html?t=nohO&s=300`: big close-up proof.

## Build and preview

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python build.py
python3 -m http.server 8765
```

Then open http://127.0.0.1:8765/specimen/.

## Use on a website

```css
@font-face {
  font-family: "Senna Display";
  src: url("/fonts/SennaDisplay-Regular.woff2") format("woff2");
  font-display: swap;
}
h1, h2 { font-family: "Senna Display", Georgia, serif; letter-spacing: -0.01em; }
```

## Current glyph set (v0.3)

- Lowercase: the full alphabet, `a` to `z`.
- Capitals: the full alphabet, `A` to `Z`.
- Punctuation: `. ,` and space.

Curves are built from true ellipses: rings (an ellipse minus a counter),
ellipses run off along straight pen-angle tangents into stems, and bowls
joined by straight spines tangent to both (s, S). Stroke ends are cut on the
shared pen angle (`PEN`), finish in teardrops (a, J), or thicken into
flat-faced beaks (s, S, C, G). Crossbars rise at the pen angle and flare at
their ends. f and j still use `nib_stroke`, which sweeps a flat pen along a
curve.

Thin strokes share two weights in `params.py`: `THIN` (18) for lowercase bars,
links, arches and bowls, and `CAP_THIN` (19) for capital crossbars and bowls.
Change either to lighten or darken the hairlines across the whole alphabet.
