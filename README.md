# Senna Display

A personal display serif for headlines, defined entirely in code. The feel
(high contrast, sharp bracketed wedge serifs, large x-height, tight spacing) is
inspired by the headline faces on sites like tako.ai, but every outline here
is original.

## Layout

- `font/params.py`: the shared design settings (metrics, stem weights, serif shape, spacing). Start here.
- `font/draw.py`: drawing primitives (contours, ellipses, boolean union/cut).
- `font/parts.py`: reusable letter parts (serifs, arches, bowls, ball terminals).
- `font/glyphs.py`: one function per glyph.
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

## Current glyph set (v0.1)

`H I O L E F T`, `n h m u l i r o c e d b p q`, `. ,` and space.
