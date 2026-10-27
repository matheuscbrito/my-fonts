"""Build the font: draw every glyph, place it between its sidebearings,
and write OTF + WOFF2 to dist/."""
import os

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

from font import params as P
from font.glyphs import GLYPHS

DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")


def notdef():
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


def build():
    order = [".notdef"]
    cmap = {}
    charstrings = {}
    metrics = {}

    w, lsb, cs = notdef()
    charstrings[".notdef"] = cs
    metrics[".notdef"] = (w, lsb)

    for name, (uni, lsb, rsb, draw) in GLYPHS.items():
        path = draw().path
        if path.bounds and path.bounds != (0, 0, 0, 0):
            x_min, _, x_max, _ = path.bounds
            width = round(x_max - x_min + lsb + rsb)
            pen = T2CharStringPen(width, None)
            path.draw(TransformPen(pen, (1, 0, 0, 1, lsb - x_min, 0)))
        else:
            width = lsb + rsb
            pen = T2CharStringPen(width, None)
        order.append(name)
        cmap[uni] = name
        charstrings[name] = pen.getCharString()
        metrics[name] = (width, lsb)

    family = P.FAMILY
    ps_name = family.replace(" ", "") + "-" + P.STYLE

    fb = FontBuilder(P.UPM, isTTF=False)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupCFF(ps_name, {"FullName": family + " " + P.STYLE}, charstrings, {})
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=P.ASC + 60, descent=P.DESC - 40)
    fb.setupNameTable({
        "familyName": family,
        "styleName": P.STYLE,
        "uniqueFontIdentifier": ps_name + "-" + P.VERSION,
        "fullName": family + " " + P.STYLE,
        "psName": ps_name,
        "version": "Version " + P.VERSION,
    })
    fb.setupOS2(
        version=4,
        sTypoAscender=P.ASC, sTypoDescender=P.DESC, sTypoLineGap=200,
        usWinAscent=P.ASC + 60, usWinDescent=-(P.DESC - 40),
        sxHeight=P.XH, sCapHeight=P.CAP, usWeightClass=400,
        fsSelection=0x40 | 0x80,  # REGULAR, USE_TYPO_METRICS
    )
    fb.setupPost()

    os.makedirs(DIST, exist_ok=True)
    otf = os.path.join(DIST, ps_name + ".otf")
    fb.save(otf)

    font = TTFont(otf)
    font.flavor = "woff2"
    woff2 = os.path.join(DIST, ps_name + ".woff2")
    font.save(woff2)
    print("built %d glyphs -> %s, %s" % (len(order), otf, woff2))


if __name__ == "__main__":
    build()
