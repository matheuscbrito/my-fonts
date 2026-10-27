"""Glyph definitions. Each function draws one letter from shared parts;
the build script places it between its sidebearings."""
import math

from .draw import Glyph, contour, ellipse, rect
from .params import (ARCH_THIN, ASC, BAR_FLARE, BAR_TIP, CAP, CAP_HAIR, CAP_OV, CAP_SB_ROUND, CAP_SERIF_TIP,
                     CAP_SB_STRAIGHT, CAP_STEM, DESC, HAIR, M_COUNTER,
                     K_OUT, N_COUNTER, O_THIN, OV, PEN, SB_ROUND, SB_STRAIGHT, SERIF, SPACE, STEM,
                     XH)
from .parts import (arch, bowl, cap_foot, cap_head, diag, drop, flared_diag, foot_serif,
                    half_plane, head_serif, intersect, nib_dot, nib_stroke, pen_bar,
                    pen_ellipse, pen_line_y, pen_side, ring, spur, tangent)

GLYPHS = {}  # name -> (unicode, lsb, rsb, draw function)


def glyph(name, uni, lsb, rsb):
    def register(fn):
        GLYPHS[name] = (uni, lsb, rsb, fn)
        return fn
    return register


# ---------------------------------------------------------------- lowercase

def _stem(x0, y0, top, head=True, foot=True, foot_left=True, foot_right=True):
    """foot: True for a flared serif, "spur" / "spur_left" for a diagonal
    nib-cut ending pointing right / left, False for none."""
    x1 = x0 + STEM
    spurred = foot in ("spur", "spur_left")
    g = Glyph().add(rect(x0, y0 + (60 if spurred else 0), x1, top - (60 if head else 0)))
    if head:
        g.add(head_serif(x0, x1, top))
    if foot == "spur":
        g.add(spur(x0, x1, y0))
    elif foot == "spur_left":
        g.add(spur(x0, x1, y0).mirror_x((x0 + x1) / 2))
    elif foot:
        g.add(foot_serif(x0, x1, y0, left=foot_left, right=foot_right))
    return g


def _n(top_left):
    xr0 = STEM + N_COUNTER
    xr1 = xr0 + STEM
    return Glyph().add(
        _stem(0, 0, top_left),
        rect(xr0, 0, xr1, XH - 250),
        foot_serif(xr0, xr1),
        arch(STEM, xr0, xr1, XH),
    )


@glyph("n", 0x6E, SB_STRAIGHT, SB_STRAIGHT)
def n():
    return _n(XH)


@glyph("h", 0x68, SB_STRAIGHT, SB_STRAIGHT)
def h():
    return _n(ASC)


@glyph("m", 0x6D, SB_STRAIGHT, SB_STRAIGHT)
def m():
    x1 = STEM + M_COUNTER
    x2 = x1 + STEM + M_COUNTER
    return Glyph().add(
        _stem(0, 0, XH),
        rect(x1, 0, x1 + STEM, XH - 250), foot_serif(x1, x1 + STEM),
        rect(x2, 0, x2 + STEM, XH - 250), foot_serif(x2, x2 + STEM),
        arch(STEM, x1, x1 + STEM, XH),
        arch(x1 + STEM, x2, x2 + STEM, XH),
    )


@glyph("u", 0x75, SB_STRAIGHT, SB_STRAIGHT)
def u():
    xr0 = STEM + N_COUNTER
    xr1 = xr0 + STEM
    bottom = arch(STEM, xr0, xr1, XH).rotate(180, xr1 / 2, XH / 2)
    return Glyph().add(
        _stem(0, 200, XH, foot=False),
        _stem(xr0, 0, XH, foot="spur"),
        bottom,
    )


@glyph("l", 0x6C, SB_STRAIGHT, SB_STRAIGHT)
def l():
    return _stem(0, 0, ASC)


@glyph("i", 0x69, SB_STRAIGHT, SB_STRAIGHT)
def i():
    return Glyph().add(_stem(0, 0, XH), nib_dot(STEM / 2, XH + 190, 132))


@glyph("r", 0x72, SB_STRAIGHT, SB_ROUND - 10)
def r():
    # The arm is the n's arch, narrowed, with its shoulder cut off on the pen
    # diagonal, so r and n share one curve.
    xr0 = STEM + 132
    xr1 = xr0 + STEM * 0.85
    k = math.tan(PEN)
    y_cut = XH * 0.82  # height of the cut at the shoulder's outer edge: the arm ends up top
    keep = contour(
        (STEM - 5, y_cut - (xr1 - STEM + 5) * k),
        (xr1 + 60, y_cut + 60 * k),
        (xr1 + 60, XH + 100),
        (STEM - 5, XH + 100),
    )
    shoulder = Glyph().add(arch(STEM, xr0, xr1, XH)).clip(keep)
    return Glyph().add(
        _stem(0, 0, XH),
        foot_serif(0, STEM, reach=SERIF * 1.3, left=False),
        shoulder,
    )


@glyph("o", 0x6F, SB_ROUND, SB_ROUND)
def o():
    rx = 250  # o is nearly a circle (ry = 249)
    ry = XH / 2 + OV
    return ring(rx, XH / 2, rx, ry, rx - STEM * 0.98)


@glyph("c", 0x63, SB_ROUND, SB_ROUND - 6)
def c():
    rx = 232
    ry = XH / 2 + OV
    cx = rx
    g = ring(cx, XH / 2, rx, ry, rx - STEM * 0.86, dx_in=14)
    # Both ends cut on the nib diagonal.
    return g.cut(contour((cx + 20, XH * 0.36), (cx + rx + 30, XH * 0.14),
                         (cx + rx + 30, XH * 0.82), (cx + 20, XH * 0.58)))


@glyph("e", 0x65, SB_ROUND, SB_ROUND - 4)
def e():
    rx = 236
    ry = XH / 2 + OV
    cx = rx
    rx_in = rx - STEM * 0.88
    dx_in = 12
    bar0 = XH * 0.50  # bottom of the bar at the centre; it rises at the pen angle
    k = math.tan(PEN)
    g = ring(cx, XH / 2, rx, ry, rx_in, thin=O_THIN + 5, dx_in=dx_in)
    # The bar runs from where its underside meets the counter (left flare grows
    # out of the bowl) to where it meets the outer contour (the heavy tip).
    ry_in = ry - O_THIN - 5

    def yb(x):
        return bar0 + (x - cx) * k

    x_in = next(x for x in range(int(cx - rx), int(cx))
                if ((x - cx - dx_in) / rx_in) ** 2 + ((yb(x) - XH / 2) / ry_in) ** 2 < 1)
    x_out = next(x for x in range(int(cx + rx), int(cx), -1)
                 if ((x - cx) / rx) ** 2 + ((yb(x) - XH / 2) / ry) ** 2 < 1)
    # Open the aperture first, then lay the bar over it so the tip's flare
    # hangs into the opening.
    x_l, x_r = cx + 10, cx + rx + 30
    g.cut(contour((x_l, yb(x_l)), (x_r, yb(x_r)), (x_r, XH * 0.14), (x_l, XH * 0.34)))
    bar = Glyph().add(pen_bar(x_in, x_out, bar0, HAIR + 7, pivot=cx,
                              flare=(BAR_FLARE * 0.8, BAR_TIP * 0.45), flare_len=120, ext=(40, 30)))
    g.add(bar.clip(ellipse(cx, XH / 2, rx - 1, ry - 1, K_OUT)))
    return g


BOWL = 384  # from the stem's inner edge to the bowl's far side


@glyph("d", 0x64, SB_ROUND, SB_STRAIGHT)
def d():
    return Glyph().add(bowl(0, -1, BOWL, XH), _stem(0, 0, ASC, foot="spur"))


@glyph("b", 0x62, SB_STRAIGHT, SB_ROUND)
def b():
    return Glyph().add(_stem(0, 0, ASC, foot="spur_left"), bowl(STEM, 1, BOWL, XH))


@glyph("p", 0x70, SB_STRAIGHT, SB_ROUND)
def p():
    return Glyph().add(_stem(0, DESC, XH), bowl(STEM, 1, BOWL, XH))


@glyph("q", 0x71, SB_ROUND, SB_STRAIGHT)
def q():
    return Glyph().add(bowl(0, -1, BOWL, XH), rect(0, DESC, STEM, XH - OV),
                       foot_serif(0, STEM, DESC))


# ------------------------------------------------- lowercase: pen-drawn curves

NIB_Y = HAIR / 2  # a nib's centre sits this far inside a horizontal edge


@glyph("t", 0x74, SB_STRAIGHT, SB_ROUND - 14)
def t():
    s = STEM / 2
    top = XH + 140
    # Hook: the lower half of a ring whose outer and inner edges leave the
    # stem's two sides straight down, thinning round the bottom and ending
    # in a pen-angle cut.
    rx, ry, right = 150, 164, 30
    cy = ry - OV
    dx_in = (STEM - right) / 2
    hook = ring(rx, cy, rx, ry, rx + dx_in - STEM, thin=O_THIN + 9, dx_in=dx_in)
    hook.clip(rect(-10, -100, 2 * rx + 10, cy)).cut(pen_side(rx + 20, 2 * rx + 20, 2 * rx, 92))
    stem = Glyph().add(rect(0, cy - 1, STEM, top + 10)).clip(pen_side(-10, STEM + 10, STEM, top, above=False))
    return Glyph().add(
        stem, hook,
        pen_bar(-78, STEM + 150, XH - 44, HAIR + 8, pivot=s,
                flare=(BAR_FLARE * 0.5, BAR_TIP * 0.55), flare_len=80),
    )


@glyph("f", 0x66, SB_STRAIGHT, 0)
def f():
    s = STEM / 2
    yt = ASC + OV - NIB_Y
    hook = nib_stroke([
        ((s, ASC - 280), (s, ASC - 80), (s + 40, yt), (s + 140, yt)),
        ((s + 140, yt), (s + 212, yt), (s + 250, ASC - 30), (s + 255, ASC - 135)),
    ])
    hook.clip(Glyph().add(pen_side(s + 150, s + 400, s + 255 + 53, ASC - 55))
              .add(rect(-200, -400, s + 150, ASC + 200)))
    return Glyph().add(
        rect(0, 0, STEM, ASC - 230), foot_serif(0, STEM, reach=SERIF * 1.2), hook,
        pen_bar(-80, STEM + 140, XH - 34, HAIR + 4, pivot=s,
                flare=(BAR_FLARE * 0.5, BAR_TIP * 0.55), flare_len=80),
    )


@glyph("j", 0x6A, SB_STRAIGHT - 20, SB_STRAIGHT)
def j():
    s = STEM / 2
    yb = DESC - OV + NIB_Y
    hook = nib_stroke([
        ((s, 120), (s, DESC + 60), (s - 40, yb), (s - 120, yb)),
        ((s - 120, yb), (s - 180, yb), (s - 208, DESC + 30), (s - 212, DESC + 100)),
    ])
    hook.clip(Glyph().add(pen_side(s - 400, s + 400, s - 212 - 53, DESC + 72, above=False))
              .add(rect(-10, DESC + 100, STEM + 10, XH)))
    return Glyph().add(_stem(0, 100, XH, foot=False), hook, nib_dot(STEM / 2, XH + 190, 132))


@glyph("a", 0x61, SB_ROUND, SB_STRAIGHT - 10)
def a():
    xs = 250  # left edge of the stem
    k = math.tan(PEN)
    # Hook: the top of a ring like c's, swelling from a hairline crown into
    # a heavy shoulder, and ending on the left in a teardrop.
    rx, ry, left = 186, 150, 40
    cx, cy = xs + STEM - rx, XH + OV - ry
    hook = ring(cx, cy, rx, ry, rx - (STEM + left) / 2, thin=ARCH_THIN + 3, dx_in=(left - STEM) / 2)
    hook.clip(rect(cx - rx - 10, cy, xs + STEM + 10, XH + 50)).cut(rect(cx - rx - 10, cy - 10, cx, cy + 50))
    rb = 58  # teardrop: a ball whose tail runs up into the hook's hairline
    ball = drop(cx - rx + rb + 4, cy + 30, rb, angle=-40, length=rb * 2.3)
    # Bowl: a wide ellipse whose top runs off on a pen-angle tangent into
    # the stem. The counter is narrow and climbs into the stem more steeply,
    # so the diagonal is a hairline at the stem and swells to the left.
    rx, ry = 150, 140
    cx, cy = xs - 110, ry - OV
    xj = xs + STEM / 2
    x0, x1, y0 = cx - rx + STEM * 1.18, xs + 2, -OV + O_THIN + 4
    rxi, cxi = (x1 - x0) / 2, (x0 + x1) / 2
    steep = PEN * 1.9
    gap = pen_line_y(cx, cy, rx, ry, xs) - ARCH_THIN - 4  # counter tip height at the stem
    lo, hi = 20, ry * 2
    for _ in range(30):
        mid = (lo + hi) / 2
        if pen_line_y(cxi, y0 + mid, rxi, mid, xs, steep) < gap:
            lo = mid
        else:
            hi = mid
    bowl_ = pen_ellipse(cx, cy, rx, ry, xj).cut(pen_ellipse(cxi, y0 + lo, rxi, lo, xj, steep))
    # Stem foot: one long pen-angle cut from below the bowl's join out to a
    # sharp spur, its upper edge running straight back into the stem.
    xt = xs + STEM + 78
    foot = contour((xs, -OV), (xt, -OV + (xt - xs) * k), (xs + STEM, 92), (xs, 92))
    return Glyph().add(bowl_, hook, ball, rect(xs, 60, xs + STEM, XH + OV - 150 + 1), foot)


@glyph("s", 0x73, SB_ROUND, SB_ROUND)
def s():
    # Two elliptical bowls joined by a straight spine: each bowl's outer
    # ellipse touches one edge of the spine and its counter the other, so
    # every edge runs on smoothly. The lower half is the upper turned 180°.
    C = (190, XH / 2)
    W = 98                    # spine weight, measured across
    fall = math.radians(36)   # the spine falls to the right at this angle
    n = (math.sin(fall), math.cos(fall))
    nC = n[0] * C[0] + n[1] * C[1]
    rx, ry = 168, 136
    cy = XH + OV - ry
    s_o = math.hypot(rx * n[0], ry * n[1])
    cx = (nC - W / 2 + s_o - n[1] * cy) / n[0]
    t_o = tangent(cx, cy, rx, ry, (-n[0], -n[1]))[0]
    # Counter: a hairline top, heavy left side, lighter right side.
    left, right = 92, 34
    rxi, cxi = rx - (left + right) / 2, cx + (left - right) / 2
    top_i = XH + OV - HAIR - 9
    lo, hi = 20, ry
    for _ in range(30):
        mid = (lo + hi) / 2
        if -tangent(cxi, top_i - mid, rxi, mid, (-n[0], -n[1]))[1] > nC + W / 2:
            lo = mid
        else:
            hi = mid
    cyi = top_i - lo
    t_i = tangent(cxi, cyi, rxi, lo, (-n[0], -n[1]))[0]
    upper = Glyph().add(ellipse(cx, cy, rx, ry)).cut(ellipse(cxi, cyi, rxi, lo))
    # Drop the bowl's bottom past the spine joint, and cut the terminal.
    upper.cut(Glyph().add(half_plane(t_i, t_o)).clip(rect(-1000, -1000, 1000, cy)))
    # Beak: the terminal thickens into a slab with a flat outer face, its
    # foot cut on the pen angle.
    xe, yc = cx + rx * 0.94, cy - ry * 0.04
    upper.add(Glyph().add(pen_side(xe - 40, xe, xe, yc)).clip(ellipse(cx, cy, rx, ry)))
    upper.cut(pen_side(cx + 20, cx + rx + 40, xe, yc, above=False), rect(xe, yc - 200, xe + 100, cy + ry))
    turn = lambda p: (2 * C[0] - p[0], 2 * C[1] - p[1])
    spine = contour(t_o, turn(t_i), turn(t_o), t_i)
    return Glyph().add(upper, upper.turn(*C), spine)


@glyph("g", 0x67, SB_ROUND, SB_ROUND - 10)
def g():
    ry = 168
    cy = XH + OV - ry
    upper = ring(172, cy, 156, ry, 156 - STEM * 0.9, thin=O_THIN + 5)
    # Ear: a pen-angle bar off the bowl's shoulder, swelling at its tip.
    ear = pen_bar(285, 400, XH - 22, HAIR + 6, pivot=285, flare=(0, BAR_TIP * 0.6),
                  flare_len=60, ext=(40, 0))
    # Lower loop: a ring heavy on the right, joined by a straight hairline.
    top, bot = 74, DESC - OV
    ryl = (top - bot) / 2
    loop = ring(228, top - ryl, 214, ryl, 214 - STEM * 0.72, thin=O_THIN + 5, dx_in=-STEM * 0.28)
    link = flared_diag((146, cy - ry + 10), (120, 40), HAIR + 8, 34)
    return Glyph().add(upper, ear, link, loop)


# ------------------------------------------------- lowercase: straight diagonals

DIAG = STEM * 1.1     # thick diagonal, measured horizontally
DIAG_HAIR = HAIR * 2  # thin diagonal


def _v(x0, span=430, apex=0.52, left_serif=True, right_serif=True, bottom=None, hair=DIAG_HAIR):
    """A v from a thick left and a thin right diagonal meeting in a point."""
    xa = x0 + DIAG / 2
    xb = x0 + span - hair / 2
    xv = x0 + span * apex
    yv = -OV * 1.6 if bottom is None else bottom
    A, B = (xa - DIAG / 2, XH), (xa + DIAG / 2, XH)
    D, E = (xb - hair / 2, XH), (xb + hair / 2, XH)
    V = (xv, yv)
    C = intersect(B, (B[0] + V[0] - A[0], B[1] + V[1] - A[1]),
                  D, (D[0] + V[0] - E[0], D[1] + V[1] - E[1]))
    g = Glyph().add(contour(A, V, E, D, C, B))
    if left_serif:
        g.add(foot_serif(A[0], B[0], reach=SERIF).mirror_y(XH / 2))
    if right_serif:
        g.add(foot_serif(D[0], E[0], reach=SERIF * 0.8).mirror_y(XH / 2))
    return g, V, E


@glyph("v", 0x76, SB_STRAIGHT - 4, SB_STRAIGHT - 4)
def v():
    return _v(0)[0]


@glyph("w", 0x77, SB_STRAIGHT - 4, SB_STRAIGHT - 4)
def w():
    first, _, _ = _v(0, span=380, right_serif=False)
    offset = 380 - DIAG_HAIR / 2 - DIAG / 2  # second thick starts on the first thin
    second, _, _ = _v(offset, span=380)
    return Glyph().add(first, second)


@glyph("y", 0x79, SB_STRAIGHT - 4, SB_STRAIGHT - 4)
def y():
    span = 430
    hair = DIAG_HAIR + 6
    body, V, E = _v(0, span=span, bottom=-OV, hair=hair)
    # The thin stroke carries on past the point into the descender and turns
    # into a tail: an outer ellipse touching the stroke's right edge and a
    # counter touching its left edge, so both edges run on without a bend.
    dx = (V[0] - E[0]) / (XH - V[1])  # horizontal drift per unit of drop
    nrm = (1, dx)                     # outward normal of the stroke's right side
    xr = E[0] + dx * XH               # right edge at y = 0 (the left edge is hair further left)

    def touching(rx, ry, cy, shift):
        # centre x that makes the ellipse touch the edge line x = xr - shift + dx*y
        h_line = nrm[0] * (xr - shift)
        return (h_line - nrm[1] * cy - math.hypot(rx * nrm[0], ry * nrm[1])) / nrm[0]

    rx, ry = 120, 108
    cy = DESC - OV + ry
    cx = touching(rx, ry, cy, 0)
    rxi, ryi = 50, ry - 22
    cyi = DESC - OV + 16 + ryi
    cxi = touching(rxi, ryi, cyi, hair)
    t_o = tangent(cx, cy, rx, ry, nrm)[0]
    t_i = tangent(cxi, cyi, rxi, ryi, nrm)[0]
    tail = Glyph().add(ellipse(cx, cy, rx, ry)).cut(ellipse(cxi, cyi, rxi, ryi))
    tail.clip(rect(cx - rx - 10, DESC - 100, cx + rx + 10, cy + 20))
    tail.cut(Glyph().add(half_plane(t_i, t_o)).clip(rect(t_i[0] - 10, DESC - 100, cx + rx + 10, cy + ry)))
    tail.cut(pen_side(cx - rx - 20, cx - 10, cx - rx, cy - 4))
    tail_line = Glyph().add(diag((E[0] - hair / 2, XH), (E[0] - hair / 2 + dx * (XH - DESC),
                                                              DESC), hair))
    tail_line.cut(half_plane(t_o, t_i))
    return Glyph().add(body, tail_line, tail)


@glyph("x", 0x78, SB_STRAIGHT - 6, SB_STRAIGHT - 6)
def x():
    wd = 440
    thick = diag((DIAG / 2 + 4, XH), (wd - DIAG / 2 - 4, 0), DIAG)
    thin = diag((wd - DIAG_HAIR / 2 - 12, XH), (DIAG_HAIR / 2 + 12, 0), DIAG_HAIR)
    t0, t1 = 4, DIAG + 4
    h0, h1 = wd - DIAG_HAIR - 12, wd - 12
    return Glyph().add(
        thick, thin,
        foot_serif(t0, t1, reach=SERIF).mirror_y(XH / 2),
        foot_serif(h0, h1, reach=SERIF * 0.8).mirror_y(XH / 2),
        foot_serif(12, 12 + DIAG_HAIR, reach=SERIF * 0.8),
        foot_serif(wd - DIAG - 4, wd - 4, reach=SERIF),
    )


@glyph("k", 0x6B, SB_STRAIGHT, SB_STRAIGHT - 6)
def k():
    arm_top = STEM + 250
    arm = diag((arm_top, XH), (STEM - 10, XH * 0.22), DIAG_HAIR)
    # The leg grows out of the arm: trim it along the arm's left edge.
    l1 = (arm_top - DIAG_HAIR / 2, XH)
    l2 = (STEM - 10 - DIAG_HAIR / 2, XH * 0.22)
    below_arm = contour(l2, l1, (l1[0] + 1000, l1[1]), (l1[0] + 1000, -500), (l2[0], -500))
    leg = Glyph().add(diag((STEM + 60, XH * 0.70), (STEM + 262, 0), DIAG)).clip(below_arm)
    right_of_stem = rect(STEM - 2, -50, 900, XH + 50)
    return Glyph().add(
        _stem(0, 0, ASC),
        Glyph().add(arm, leg).clip(right_of_stem),
        foot_serif(arm_top - DIAG_HAIR / 2, arm_top + DIAG_HAIR / 2, reach=SERIF * 0.9).mirror_y(XH / 2),
        foot_serif(STEM + 262 - DIAG / 2, STEM + 262 + DIAG / 2, reach=SERIF),
    )


@glyph("z", 0x7A, SB_STRAIGHT, SB_STRAIGHT)
def z():
    wd = 400
    bar = HAIR + 12
    slant = STEM * 1.3  # the thick diagonal, measured horizontally
    return Glyph().add(
        rect(0, XH - bar, wd, XH),
        contour((wd - slant, XH - bar), (wd, XH - bar), (slant, bar), (0, bar)),
        rect(0, 0, wd, bar),
        arm_serif(wd, 0, bar, 110).mirror_x(wd / 2).mirror_y(XH / 2),
        arm_serif(wd, 0, bar, 120),
    )


# ----------------------------------------------------------------- capitals

def _cap_stem(x0, head_left=True, head_right=True, foot_left=True, foot_right=True):
    x1 = x0 + CAP_STEM
    return Glyph().add(
        rect(x0, 0, x1, CAP),
        cap_head(x0, x1, CAP, head_left, head_right),
        cap_foot(x0, x1, foot_left, foot_right),
    )


def arm_serif(xe, y, t, h, tip=CAP_SERIF_TIP + 2, bracket=120):
    """Vertical wedge at the right end of a horizontal arm whose bottom edge
    is at y and thickness t; it rises to y + h."""
    return contour(
        (xe, y), (xe, y + h), (xe - tip, y + h),
        ((xe - tip - 10, y + t + (h - t) * 0.45), (xe - bracket * 0.7, y + t + 4), (xe - bracket, y + t)),
        (xe - bracket, y),
    )


ARM = CAP_HAIR + 8  # horizontal arms of E F L T


@glyph("H", 0x48, CAP_SB_STRAIGHT, CAP_SB_STRAIGHT)
def H():
    w = 590
    bar = CAP * 0.49
    return Glyph().add(
        _cap_stem(0), _cap_stem(w - CAP_STEM),
        pen_bar(CAP_STEM, w - CAP_STEM, bar, CAP_HAIR + 2, ext=(CAP_STEM / 2, CAP_STEM / 2)),
    )


@glyph("I", 0x49, CAP_SB_STRAIGHT, CAP_SB_STRAIGHT)
def I():
    return _cap_stem(0)


@glyph("L", 0x4C, CAP_SB_STRAIGHT, CAP_SB_STRAIGHT - 6)
def L():
    w = 450
    return Glyph().add(
        _cap_stem(0, foot_right=False),
        rect(0, 0, w, ARM),
        arm_serif(w, 0, ARM, 160),
    )


def _e_arms(top_w, mid_w):
    top = arm_serif(top_w, 0, ARM, 150).mirror_y(CAP / 2)
    mid0 = CAP * 0.48  # bottom of the middle arm, at the centre of its visible part
    return Glyph().add(
        rect(0, CAP - ARM, top_w, CAP), top,
        pen_bar(CAP_STEM, mid_w, mid0, CAP_HAIR + 2, pivot=(CAP_STEM + mid_w) / 2,
                ext=(CAP_STEM / 2, 0)),
    )


@glyph("E", 0x45, CAP_SB_STRAIGHT, CAP_SB_STRAIGHT - 6)
def E():
    w = 460
    return Glyph().add(
        _cap_stem(0, head_right=False, foot_right=False),
        _e_arms(430, 370),
        rect(0, 0, w, ARM), arm_serif(w, 0, ARM, 170),
    )


@glyph("F", 0x46, CAP_SB_STRAIGHT, CAP_SB_STRAIGHT - 10)
def F():
    return Glyph().add(_cap_stem(0, head_right=False), _e_arms(430, 370))


@glyph("T", 0x54, CAP_SB_STRAIGHT - 10, CAP_SB_STRAIGHT - 10)
def T():
    w = 580
    s0 = (w - CAP_STEM) / 2
    right = arm_serif(w, 0, ARM, 150).mirror_y(CAP / 2)
    return Glyph().add(
        rect(0, CAP - ARM, w, CAP), right, right.mirror_x(w / 2),
        rect(s0, 0, s0 + CAP_STEM, CAP - 10), cap_foot(s0, s0 + CAP_STEM),
    )


@glyph("O", 0x4F, CAP_SB_ROUND, CAP_SB_ROUND)
def O():
    rx = 364
    ry = CAP / 2 + CAP_OV
    return ring(rx, CAP / 2, rx, ry, rx - CAP_STEM * 1.02, thin=CAP_HAIR)


# -------------------------------------------------------------- punctuation

DOT = 52


@glyph("period", 0x2E, 34, 40)
def period():
    return Glyph().add(nib_dot(DOT, DOT + 4, DOT * 2.1))


@glyph("comma", 0x2C, 34, 40)
def comma():
    cx = DOT
    tail = contour(
        (cx + DOT - 2, DOT + 6),
        ((cx + DOT + 4, -20), (cx + 20, -110), (cx - 36, -165)),
        (cx - 46, -152),
        ((cx - 6, -110), (cx + 12, -50), (cx + 4, 10)),
    )
    return Glyph().add(nib_dot(cx, DOT + 4, DOT * 2.1), tail)


@glyph("space", 0x20, 0, SPACE)
def space():
    return Glyph()
