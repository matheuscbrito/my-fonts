"""Reusable letter parts: serifs, arches, bowls, terminals."""
import math

import pathops

from .draw import KAPPA, Glyph, circle, contour, ellipse
from .params import (ARCH_THIN, BRACKET, CAP_BRACKET, CAP_SERIF, CAP_SERIF_TIP,
                     HEAD, HEAD_SLOPE, K_IN, K_OUT, O_THIN, OV, SERIF,
                     BAR_FLARE, BAR_FLARE_LEN, BAR_TIP, HAIR, PEN, SERIF_TIP, STEM, STRESS, THIN)


def foot_serif(x0, x1, y=0, reach=SERIF, tip=SERIF_TIP, bracket=BRACKET,
               left=True, right=True):
    """Flared wedge serif sitting on y, for a stem spanning x0..x1. The flanks
    run almost straight at the pen angle, like a broad-nib pen lifting off."""
    rise = bracket - tip
    c = [(x0, y + bracket)]
    if left:
        c += [((x0 - reach * 0.33, y + tip + rise * 0.62), (x0 - reach * 0.66, y + tip + rise * 0.28), (x0 - reach, y + tip)),
              (x0 - reach, y)]
    else:
        c += [(x0, y)]
    if right:
        c += [(x1 + reach, y), (x1 + reach, y + tip),
              ((x1 + reach * 0.66, y + tip + rise * 0.28), (x1 + reach * 0.33, y + tip + rise * 0.62), (x1, y + bracket))]
    else:
        c += [(x1, y), (x1, y + bracket)]
    return contour(*c)


def spur(x0, x1, y=0, reach=SERIF * 0.7):
    """Stem ending cut on the nib diagonal: the bottom edge slopes down to a
    sharp point past the right side. Stems using it start at y + 60."""
    return contour(
        (x0, y + 52),
        ((x0 + (x1 - x0) * 0.5, y + 24), (x1 + reach * 0.5, y + 3), (x1 + reach, y)),
        (x1 + reach, y + 5),
        ((x1 + reach * 0.5, y + 12), (x1, y + 30), (x1, y + 74)),
        (x0, y + 74),
    )


def nib_dot(cx, cy, size):
    """A broad-nib dab for i and punctuation: a box whose top and bottom are
    sheared along the pen angle."""
    w, h = size * 0.9, size * 1.15
    d = w * math.tan(PEN)
    return contour(
        (cx - w / 2, cy - h / 2),
        (cx + w / 2, cy - h / 2 + d),
        (cx + w / 2, cy + h / 2),
        (cx - w / 2, cy + h / 2 - d),
    )


def pen_bar(x0, x1, y, t, pivot=None, angle=PEN, flare=(BAR_FLARE, BAR_TIP),
            flare_len=BAR_FLARE_LEN, ext=(0, 0)):
    """A crossbar of vertical thickness t, rising to the right at the pen
    angle. Its bottom edge passes through y at x = pivot (default: middle).
    Like the l's head wedge, the top edge runs straight while the underside
    swells toward the ends: flare = (left, right) extra thickness, reached
    over flare_len. ext = (left, right) continues the bar at full flare past
    x0/x1, to bury it in a stem or bowl."""
    pivot = (x0 + x1) / 2 if pivot is None else pivot
    k = math.tan(angle)
    f0, f1 = flare
    e0, e1 = ext
    flare_len = min(flare_len, (x1 - x0) / 2)  # short bars: the two flares meet

    def yb(x):
        return y + (x - pivot) * k

    a, b = x0 + flare_len, x1 - flare_len
    return contour(
        (x0 - e0, yb(x0 - e0) - f0),
        (x0, yb(x0) - f0),
        ((x0 + flare_len * 0.18, yb(x0 + flare_len * 0.18) - f0 * 0.4), (x0 + flare_len * 0.5, yb(x0 + flare_len * 0.5)), (a, yb(a))),
        (b, yb(b)),
        ((x1 - flare_len * 0.5, yb(x1 - flare_len * 0.5)), (x1 - flare_len * 0.18, yb(x1 - flare_len * 0.18) - f1 * 0.4), (x1, yb(x1) - f1)),
        (x1 + e1, yb(x1 + e1) - f1),
        (x1 + e1, yb(x1 + e1) + t),
        (x0 - e0, yb(x0 - e0) + t),
    )


def cap_foot(x0, x1, left=True, right=True):
    return foot_serif(x0, x1, 0, CAP_SERIF, CAP_SERIF_TIP, CAP_BRACKET, left, right)


def cap_head(x0, x1, top, left=True, right=True):
    return cap_foot(x0, x1, left, right).mirror_y(top / 2)


def head_serif(x0, x1, top, reach=HEAD, slope=HEAD_SLOPE, tip=SERIF_TIP):
    """Diagonal wedge pointing left, the lowercase entry stroke, cut at the
    nib angle from the stem's top-right corner down to a sharp tip."""
    yt = top - slope - tip
    span = x1 - x0 + reach
    return contour(
        (x1, top),
        ((x1 - span * 0.35, top - slope * 0.30), (x0 - reach * 0.6, top - slope * 0.82), (x0 - reach, top - slope)),
        (x0 - reach, yt),
        ((x0 - reach * 0.55, yt - 12), (x0 - 8, yt - 40), (x0, yt - 72)),
        (x0, top - 240),
        (x1, top - 240),
    )


def arch(xj, xr0, xr1, top, ov=OV, thin=ARCH_THIN):
    """Shoulder of n/m/h: leaves the left stem thin at xj and lands on the
    right stem (xr0..xr1) at full weight."""
    w = xr1 - xj
    ax = xj + w * 0.50        # outer apex
    ai = xj + w * 0.47        # inner apex sits slightly left, so the right shoulder is heavier
    yo = top + ov
    yi = yo - thin
    j_out = top * 0.80
    j_in = top * 0.58
    r_out = top * 0.66
    r_in = top * 0.62
    low = top - 260
    return contour(
        (xj, j_out),
        ((xj + (ax - xj) * 0.18, j_out + (yo - j_out) * 0.62), (ax - (ax - xj) * 0.55, yo), (ax, yo)),
        ((ax + (xr1 - ax) * 0.56, yo), (xr1, r_out + (yo - r_out) * 0.56), (xr1, r_out)),
        (xr1, low),
        (xr0, low),
        (xr0, r_in),
        ((xr0, r_in + (yi - r_in) * 0.56), (ai + (xr0 - ai) * 0.56, yi), (ai, yi)),
        ((ai - (ai - xj) * 0.62, yi), (xj, j_in + (yi - j_in) * 0.30), (xj, j_in)),
    )


def _samples(shape, steps=48):
    pts = []
    for c in shape.contours:
        p0 = c[0]
        for seg in c[1:]:
            if seg[0] == "L":
                p0 = seg[1]
                pts.append(p0)
                continue
            c1, c2, p3 = seg[1:]
            for i in range(1, steps + 1):
                t = i / steps
                mt = 1 - t
                pts.append(tuple(mt ** 3 * a + 3 * mt * mt * t * b + 3 * mt * t * t * d + t ** 3 * e
                                 for a, b, d, e in zip(p0, c1, c2, p3)))
            p0 = p3
    return pts


def _min_gap(a, b):
    return min(math.hypot(p[0] - q[0], p[1] - q[1]) for p in a for q in b)


def ring(cx, cy, rx, ry, rx_in, thin=O_THIN, dx_in=0, angle=STRESS, k=K_OUT, k_in=K_IN):
    """An outer ellipse minus an inner counter. The counter is tilted by
    `angle` (the stress) and its height is solved so the thinnest point of
    the stroke is exactly `thin`. dx_in shifts the counter sideways."""
    outer = ellipse(cx, cy, rx, ry, k)
    outer_pts = _samples(outer, 24)

    def counter(ry_in):
        return ellipse(cx + dx_in, cy, rx_in, ry_in, k_in).rotate(angle, cx + dx_in, cy)

    lo, hi = ry * 0.6, ry
    for _ in range(18):
        mid = (lo + hi) / 2
        if _min_gap(_samples(counter(mid), 24), outer_pts) > thin:
            lo = mid
        else:
            hi = mid
    return Glyph().add(outer).cut(counter(lo))


def drop(x, y, r, angle=0, length=None):
    """Teardrop terminal: a ball of radius r at (x, y) whose tail points
    up, rotated counter-clockwise by `angle` degrees."""
    length = length or r * 2.4
    return contour(
        (r, 0),
        ((r, r * 0.9), (r * 0.25, length * 0.78), (0, length)),
        ((-r * 0.25, length * 0.78), (-r, r * 0.9), (-r, 0)),
        ((-r, -r * KAPPA), (-r * KAPPA, -r), (0, -r)),
        ((r * KAPPA, -r), (r, -r * KAPPA), (r, 0)),
    ).rotate(angle).translate(x, y)


def bowl(stem_edge, side, width, top, stem=STEM, ov=OV, thin=O_THIN):
    """Bowl attached to a stem (b d p q). The bowl's near side hides inside
    the stem so only thin joins show; the far side carries the weight.
    side=+1 puts the bowl right of stem_edge, -1 left of it."""
    ry = top / 2 + ov
    near_out = stem_edge - side * stem * 0.7
    far_out = stem_edge + side * width
    cx = (near_out + far_out) / 2
    rx = abs(far_out - near_out) / 2
    far_in = far_out - side * stem * 0.98
    near_in = stem_edge
    cx_in = (near_in + far_in) / 2
    rx_in = abs(far_in - near_in) / 2
    return ring(cx, top / 2, rx, ry, rx_in, thin, cx_in - cx)


def ball(cx, cy, r):
    return circle(cx, cy, r)


def _bezier(p0, c1, c2, p3, t):
    mt = 1 - t
    return tuple(mt ** 3 * a + 3 * mt * mt * t * b + 3 * mt * t * t * d + t ** 3 * e
                 for a, b, d, e in zip(p0, c1, c2, p3))


def _hull(pts):
    """Convex hull, counter-clockwise (monotone chain)."""
    pts = sorted(set(pts))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def nib_stroke(segments, width=STEM, height=THIN, angle=0, taper=(0, 0), samples=40):
    """Sweep a flat broad-nib pen (a width x height ellipse turned by
    `angle` degrees) along a chain of cubic segments (p0, c1, c2, p3).
    Strokes moving up and down come out `width` thick, sideways ones
    `height` thin, like a real pen. taper = (start, end) fractions of the
    stroke over which the nib narrows to nothing, for pen lifts."""
    centres = []
    for n, seg in enumerate(segments):
        for i in range(0 if n == 0 else 1, samples + 1):
            centres.append(_bezier(*seg, i / samples))
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -uy * height / 2, ux * height / 2
    last = len(centres) - 1

    def corners(i):
        u = i / last
        s = 1.0
        if taper[0] and u < taper[0]:
            s = max(0.12, u / taper[0])
        if taper[1] and u > 1 - taper[1]:
            s = max(0.12, (1 - u) / taper[1])
        hx, hy = ux * width * s / 2, uy * width * s / 2
        x, y = centres[i]
        # The nib is a thin ellipse: a flat rectangle would leave flat spots
        # wherever the stroke runs level or upright.
        return [(x + hx * math.cos(q) + vx * math.sin(q), y + hy * math.cos(q) + vy * math.sin(q))
                for q in (j * math.pi / 12 for j in range(24))]

    path = pathops.Path()
    pen = path.getPen()
    for i in range(last):
        hull = _hull(corners(i) + corners(i + 1))
        pen.moveTo(hull[0])
        for p in hull[1:]:
            pen.lineTo(p)
        pen.closePath()
    path.simplify(fix_winding=True)  # all hulls wind the same way: this is their union
    g = Glyph()
    g.path = path
    return g


def _bezier_tangent(p0, c1, c2, p3, t):
    mt = 1 - t
    return tuple(3 * mt * mt * (b - a) + 6 * mt * t * (d - b) + 3 * t * t * (e - d)
                 for a, b, d, e in zip(p0, c1, c2, p3))


def var_stroke(segments, widths, samples=48):
    """A stroke along a chain of cubic segments whose thickness is set by
    hand: widths[i] is the thickness at the start of segment i, and the last
    entry at the end of the chain. Thickness eases between knots, so arcs can
    go to hairline while a spine swells, for full control of contrast."""
    assert len(widths) == len(segments) + 1
    left, right = [], []
    for n, seg in enumerate(segments):
        w0, w1 = widths[n], widths[n + 1]
        for i in range(0 if n == 0 else 1, samples + 1):
            t = i / samples
            e = t * t * (3 - 2 * t)  # smoothstep
            w = w0 + (w1 - w0) * e
            x, y = _bezier(*seg, t)
            dx, dy = _bezier_tangent(*seg, t)
            d = math.hypot(dx, dy) or 1
            nx, ny = -dy / d * w / 2, dx / d * w / 2
            left.append((x + nx, y + ny))
            right.append((x - nx, y - ny))
    path = pathops.Path()
    pen = path.getPen()
    outline = left + right[::-1]
    pen.moveTo(outline[0])
    for p in outline[1:]:
        pen.lineTo(p)
    pen.closePath()
    path.simplify(fix_winding=True)  # tidy any self-overlap on tight inner curves
    g = Glyph()
    g.path = path
    return g


def pen_side(x0, x1, xr, yr, above=True, reach=2000):
    """Half-plane bounded by a line through (xr, yr) rising at the pen
    angle, spanning x0..x1: above=True keeps what is over the line. Used to
    clip stroke ends into pen-angle cuts."""
    k = math.tan(PEN)
    y0, y1 = yr + (x0 - xr) * k, yr + (x1 - xr) * k
    far = reach if above else -reach
    return contour((x0, y0), (x1, y1), (x1, yr + far), (x0, yr + far))


def tangent(cx, cy, rx, ry, n):
    """Where a line with outward unit normal n touches the ellipse, and the
    line's offset (n . p) there."""
    s = math.hypot(rx * n[0], ry * n[1])
    p = (cx + rx * rx * n[0] / s, cy + ry * ry * n[1] / s)
    return p, n[0] * cx + n[1] * cy + s


def half_plane(p, q, reach=2000):
    """Everything left of the directed line p -> q."""
    d = math.hypot(q[0] - p[0], q[1] - p[1])
    ux, uy = (q[0] - p[0]) / d * reach, (q[1] - p[1]) / d * reach
    return contour((p[0] - ux, p[1] - uy), (p[0] + ux, p[1] + uy),
                   (p[0] + ux - uy, p[1] + uy + ux), (p[0] - ux - uy, p[1] - uy + ux))


def pen_ellipse(cx, cy, rx, ry, x_end, angle=PEN):
    """An ellipse whose top-right runs off along a straight tangent rising
    at `angle` (the pen angle) to x_end, like a bowl drawn up into a stem."""
    (tx, ty), _ = tangent(cx, cy, rx, ry, (-math.sin(angle), math.cos(angle)))
    yj = ty + (x_end - tx) * math.tan(angle)
    return Glyph().add(ellipse(cx, cy, rx, ry),
                       contour((tx, ty), (x_end, yj), (x_end, cy), (cx, cy)))


def pen_line_y(cx, cy, rx, ry, x, angle=PEN):
    """Height at x of pen_ellipse's tangent line."""
    (tx, ty), _ = tangent(cx, cy, rx, ry, (-math.sin(angle), math.cos(angle)))
    return ty + (x - tx) * math.tan(angle)


def diag(top, bottom, w):
    """Straight diagonal stroke between two centre points, w wide measured
    horizontally, with horizontal ends (for v w x y k)."""
    (xt, yt), (xb, yb) = top, bottom
    return contour((xt - w / 2, yt), (xt + w / 2, yt), (xb + w / 2, yb), (xb - w / 2, yb))


def flared_diag(top, bottom, w, flare):
    """A hairline between two centre points that swells toward both ends,
    like the flared crossbars: w wide in the middle, w + flare at the ends
    (measured horizontally)."""
    (xt, yt), (xb, yb) = top, bottom
    we = w + flare
    pull = (we - 4 * w) / 6  # control offset that puts the waist at w

    def side(sign):
        ct = (xt + (xb - xt) * 0.3 - sign * pull, yt + (yb - yt) * 0.3)
        cb = (xt + (xb - xt) * 0.7 - sign * pull, yt + (yb - yt) * 0.7)
        return ct, cb

    lt, lb = side(1)
    rt, rb = side(-1)
    return contour((xt - we / 2, yt), (lt, lb, (xb - we / 2, yb)), (xb + we / 2, yb),
                   (rb, rt, (xt + we / 2, yt)))


def flared_stroke(p0, p1, w, flare0=0, flare1=0, flare_len=210):
    """A straight thin stroke between two centre points, w wide measured
    horizontally, with horizontal ends. Like the crossbars, it runs straight
    and then swells toward an end: flare0 / flare1 is the extra width at
    p0 / p1 (split evenly on both sides), reached over flare_len measured
    along y."""
    (x0, y0), (x1, y1) = p0, p1
    a = min(flare_len / abs(y1 - y0), 0.5)

    def c(t, off):
        return (x0 + (x1 - x0) * t + off, y0 + (y1 - y0) * t)

    def side(sign):
        h = sign * w / 2
        f0, f1 = sign * flare0 / 2, sign * flare1 / 2
        return [
            c(0, h + f0),
            (c(a * 0.18, h + f0 * 0.4), c(a * 0.5, h), c(a, h)),
            c(1 - a, h),
            (c(1 - a * 0.5, h), c(1 - a * 0.18, h + f1 * 0.4), c(1, h + f1)),
        ]

    left, right = side(-1), side(1)
    # right side runs back from p1 to p0
    back = [right[3][2],
            (right[3][1], right[3][0], right[2]),
            right[1][2],
            (right[1][1], right[1][0], right[0])]
    return contour(*left, *back)


def intersect(p1, p2, p3, p4):
    """Intersection of line p1-p2 with line p3-p4."""
    d = (p1[0] - p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] - p4[0])
    a = p1[0] * p2[1] - p1[1] * p2[0]
    b = p3[0] * p4[1] - p3[1] * p4[0]
    return ((a * (p3[0] - p4[0]) - (p1[0] - p2[0]) * b) / d,
            (a * (p3[1] - p4[1]) - (p1[1] - p2[1]) * b) / d)
