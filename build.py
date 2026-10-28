"""Build the font: for each style, draw every glyph, place it between its
sidebearings, and write OTF + WOFF2 to dist/."""
import importlib
import os

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

import font.glyphs
import font.kerning
import font.params
import font.parts

DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")


def notdef(P):
    w = 500
    pen = T2CharStringPen(w, None)
    for x0, y0, x1, y1, clockwise in ((50, 0, 450, P.CAP, False), (100, 50, 400, P.CAP - 50, True)):
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        if clockwise:
            pts.reverse()
        pen.moveTo(pts[0])
        for pt in pts[1:]:
            pen.lineTo(pt)
        pen.closePath()
    return w, 50, pen.getCharString()


def load(style):
    """Re-import the font modules with params set for this style."""
    os.environ["SENNA_STYLE"] = style
    for module in (font.params, font.parts, font.glyphs, font.kerning):
        importlib.reload(module)
    return font.params


def build(style):
    P = load(style)
    order = [".notdef"]
    cmap = {}
    charstrings = {}
    metrics = {}
    placed = {}  # name -> (outline in place, advance), for kerning
    y_min, y_max = P.DESC - 40, P.ASC + 60  # ink extent, so Windows clips nothing

    w, lsb, cs = notdef(P)
    charstrings[".notdef"] = cs
    metrics[".notdef"] = (w, lsb)

    for name, (uni, lsb, rsb, draw) in font.glyphs.GLYPHS.items():
        g = draw().drop_specks()
        path = g.path
        if path.bounds and path.bounds != (0, 0, 0, 0):
            # Accented letters keep their base letter's extent (Glyph.box).
            x_min, x_max = getattr(g, "box", None) or (path.bounds[0], path.bounds[2])
            y_min = min(y_min, path.bounds[1])
            y_max = max(y_max, path.bounds[3])
            width = round(x_max - x_min + lsb + rsb)
            pen = T2CharStringPen(width, None)
            path.draw(TransformPen(pen, (1, 0, 0, 1, lsb - x_min, 0)))
            placed[name] = (path.transform(1, 0, 0, 1, lsb - x_min, 0), width)
        else:
            width = lsb + rsb
            pen = T2CharStringPen(width, None)
        order.append(name)
        cmap[uni] = name
        charstrings[name] = pen.getCharString()
        metrics[name] = (width, lsb)

    family = P.FAMILY
    ps_name = family.replace(" ", "") + "-" + P.STYLE
    bold = P.STYLE == "Bold"
    # Bold pairs with a regular in the classic four-style family; other
    # weights get their own family name, grouped by the typographic names.
    legacy = (family, "Bold") if bold else (family + " " + P.STYLE, "Regular")

    fb = FontBuilder(P.UPM, isTTF=False)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupCFF(ps_name, {"FullName": family + " " + P.STYLE}, charstrings, {})
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=P.ASC + 60, descent=P.DESC - 40)
    fb.setupNameTable({
        "familyName": legacy[0],
        "styleName": legacy[1],
        "typographicFamily": family,
        "typographicSubfamily": P.STYLE,
        "uniqueFontIdentifier": ps_name + "-" + P.VERSION,
        "fullName": family + " " + P.STYLE,
        "psName": ps_name,
        "version": "Version " + P.VERSION,
    })
    fb.setupOS2(
        version=4,
        sTypoAscender=P.ASC, sTypoDescender=P.DESC, sTypoLineGap=200,
        usWinAscent=round(y_max), usWinDescent=-round(y_min),
        sxHeight=P.XH, sCapHeight=P.CAP, usWeightClass=P.WEIGHT_CLASS,
        fsSelection=(0x20 if bold else 0x40) | 0x80,  # BOLD or REGULAR, USE_TYPO_METRICS
    )
    fb.updateHead(macStyle=1 if bold else 0)
    fb.setupPost()
    addOpenTypeFeaturesFromString(fb.font, font.kerning.feature(placed))

    os.makedirs(DIST, exist_ok=True)
    otf = os.path.join(DIST, ps_name + ".otf")
    fb.save(otf)

    web = TTFont(otf)
    web.flavor = "woff2"
    woff2 = os.path.join(DIST, ps_name + ".woff2")
    web.save(woff2)
    print("built %d glyphs -> %s, %s" % (len(order), otf, woff2))


if __name__ == "__main__":
    for style in font.params.STYLES:
        build(style)
