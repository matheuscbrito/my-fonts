"""Drawing primitives: shapes made of cubic contours, merged with boolean ops."""
import math

import pathops

KAPPA = 0.5523

UNION = pathops.PathOp.UNION
DIFFERENCE = pathops.PathOp.DIFFERENCE
INTERSECTION = pathops.PathOp.INTERSECTION


class Shape:
    """A list of closed contours. Each contour is [start, seg, ...] where
    seg is ("L", point) or ("C", ctrl1, ctrl2, point)."""

    def __init__(self, contours):
        self.contours = contours

    def __add__(self, other):
        return Shape(self.contours + other.contours)

    def map(self, fn):
        out = []
        for c in self.contours:
            nc = [fn(c[0])]
            for seg in c[1:]:
                nc.append((seg[0],) + tuple(fn(p) for p in seg[1:]))
            out.append(nc)
        return Shape(out)

    def translate(self, dx=0, dy=0):
        return self.map(lambda p: (p[0] + dx, p[1] + dy))

    def mirror_x(self, axis=0):
        return self.map(lambda p: (2 * axis - p[0], p[1]))

    def mirror_y(self, axis=0):
        return self.map(lambda p: (p[0], 2 * axis - p[1]))

    def rotate(self, deg, cx=0, cy=0):
        a = math.radians(deg)
        ca, sa = math.cos(a), math.sin(a)

        def fn(p):
            x, y = p[0] - cx, p[1] - cy
            return (cx + x * ca - y * sa, cy + x * sa + y * ca)

        return self.map(fn)

    def to_path(self):
        result = pathops.Path()
        for c in self.contours:
            p = pathops.Path()
            pen = p.getPen()
            pen.moveTo(c[0])
            for seg in c[1:]:
                if seg[0] == "L":
                    pen.lineTo(seg[1])
                else:
                    pen.curveTo(*seg[1:])
            pen.closePath()
            result = pathops.op(result, p, UNION, fix_winding=True)
        return result


def contour(start, *segs):
    """Build a closed contour. A point means a line to it; a triple of
    points (ctrl1, ctrl2, end) means a cubic curve."""
    c = [tuple(start)]
    for s in segs:
        if isinstance(s[0], (int, float)):
            c.append(("L", tuple(s)))
        else:
            c.append(("C",) + tuple(tuple(p) for p in s))
    return Shape([c])


def rect(x0, y0, x1, y1):
    return contour((x0, y0), (x1, y0), (x1, y1), (x0, y1))


def ellipse(cx, cy, rx, ry, k=KAPPA):
    return contour(
        (cx + rx, cy),
        ((cx + rx, cy + ry * k), (cx + rx * k, cy + ry), (cx, cy + ry)),
        ((cx - rx * k, cy + ry), (cx - rx, cy + ry * k), (cx - rx, cy)),
        ((cx - rx, cy - ry * k), (cx - rx * k, cy - ry), (cx, cy - ry)),
        ((cx + rx * k, cy - ry), (cx + rx, cy - ry * k), (cx + rx, cy)),
    )


def circle(cx, cy, r):
    return ellipse(cx, cy, r, r)


def _as_path(item):
    if isinstance(item, Shape):
        return item.to_path()
    if isinstance(item, Glyph):
        return item.path
    return item


class Glyph:
    """Accumulates ink: add() unions shapes in, cut() removes them."""

    def __init__(self):
        self.path = pathops.Path()

    def add(self, *items):
        for item in items:
            self.path = pathops.op(self.path, _as_path(item), UNION, fix_winding=True)
        return self

    def cut(self, *items):
        for item in items:
            self.path = pathops.op(self.path, _as_path(item), DIFFERENCE, fix_winding=True)
        return self

    def drop_specks(self, min_area=40):
        """Remove stray contours smaller than min_area, left by boolean ops."""
        keep = pathops.Path()
        for c in self.path.contours:
            q = pathops.Path()
            c.draw(q.getPen())
            b = q.bounds
            if (b[2] - b[0]) * (b[3] - b[1]) >= min_area:
                c.draw(keep.getPen())
        self.path = keep
        return self

    def turn(self, cx, cy):
        """A copy turned 180 degrees around (cx, cy)."""
        g = Glyph()
        g.path = self.path.transform(-1, 0, 0, -1, 2 * cx, 2 * cy)
        return g

    def clip(self, item):
        """Keep only the ink inside item."""
        self.path = pathops.op(self.path, _as_path(item), INTERSECTION, fix_winding=True)
        return self
