# Senna Display

A personal display serif for headlines, defined entirely in code. The feel
(very high contrast, hard straight-edged wedge serifs, large x-height, tight
spacing) is inspired by geometric display serifs like the headline faces on
tako.ai, but every outline here is original.

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

## Current glyph set (v0.4)

- Lowercase: the full alphabet, `a` to `z`.
- Capitals: the full alphabet, `A` to `Z`.
- Punctuation: `. ,` and space.

Curves are built from true ellipses: rings (an ellipse minus a counter),
ellipses run off along straight pen-angle tangents into stems, and bowls
joined by straight spines tangent to both (s, S). Stroke ends are cut on the
shared pen angle (`PEN`) or thicken into blunt, flat-faced ends whose feet
are cut on the pen angle (a, c, f, g, j, s, C, G, J, S). Crossbars rise at
the pen angle and widen toward their ends.

Everything that is not a bowl is drawn in straight lines: serifs are
triangular wedges, stem heads are straight diagonal cuts, flares are straight
tapers and dots are squares. Curves appear only where a letter is round.

The a is the model for the weights in `params.py`. Curves run heavier than
stems so they read equally dark: `ROUND` (119) for lowercase, `CAP_ROUND`
(125) for capitals. Thin strokes are `THIN` (11) and `CAP_THIN` (12), with
bowls a little firmer (`O_THIN`) and crossbars and arms firmer still
(`BAR_THIN`, `CAP_BAR_THIN`), since a long hairline reads lighter than a short
one. Change any of them to shift that part of the whole alphabet.
