"""Reusable letter parts: serifs, arches, bowls, terminals."""
import math

from .draw import KAPPA, Glyph, circle, contour, ellipse
from .params import (ARCH_THIN, BRACKET, CAP_BRACKET, CAP_SERIF, CAP_SERIF_TIP,
                     HEAD, HEAD_SLOPE, K_IN, K_OUT, O_THIN, OV, SERIF,
                     BAR_FLARE, BAR_FLARE_LEN, BAR_TIP, PEN, SERIF_TIP, STEM, STRESS)


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
