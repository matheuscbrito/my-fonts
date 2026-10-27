"""Glyph definitions. Each function draws one letter from shared parts;
the build script places it between its sidebearings."""
import math

from .draw import Glyph, contour, ellipse, rect
from .params import (ARCH_THIN, ASC, BAR_FLARE, BAR_TIP, CAP, CAP_BRACKET, CAP_HAIR, CAP_OV, CAP_SB_ROUND,
                     CAP_SERIF, CAP_SERIF_TIP, CAP_THIN, THIN,
                     CAP_SB_STRAIGHT, CAP_STEM, DESC, HAIR, M_COUNTER,
                     K_OUT, N_COUNTER, O_THIN, OV, PEN, SB_ROUND, SB_STRAIGHT, SERIF, SPACE, STEM,
                     XH)
from .parts import (arch, bowl, cap_foot, cap_head, diag, drop, flared_diag, flared_stroke, foot_serif,
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
    g = ring(cx, XH / 2, rx, ry, rx_in, dx_in=dx_in)
    # The bar runs from where its underside meets the counter (left flare grows
    # out of the bowl) to where it meets the outer contour (the heavy tip).
    ry_in = ry - O_THIN

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
    bar = Glyph().add(pen_bar(x_in, x_out, bar0, THIN, pivot=cx,
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

NIB_Y = THIN / 2  # a nib's centre sits this far inside a horizontal edge


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
    hook = ring(rx, cy, rx, ry, rx + dx_in - STEM, thin=O_THIN + 4, dx_in=dx_in)
    hook.clip(rect(-10, -100, 2 * rx + 10, cy)).cut(pen_side(rx + 20, 2 * rx + 20, 2 * rx, 92))
    stem = Glyph().add(rect(0, cy - 1, STEM, top + 10)).clip(pen_side(-10, STEM + 10, STEM, top, above=False))
    return Glyph().add(
        stem, hook,
        pen_bar(-78, STEM + 150, XH - 44, THIN, pivot=s,
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
        pen_bar(-80, STEM + 140, XH - 34, THIN, pivot=s,
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
    hook = ring(cx, cy, rx, ry, rx - (STEM + left) / 2, thin=ARCH_THIN + 2, dx_in=(left - STEM) / 2)
    hook.clip(rect(cx - rx - 10, cy, xs + STEM + 10, XH + 50)).cut(rect(cx - rx - 10, cy - 10, cx, cy + 50))
    rb = 58  # teardrop: a ball whose tail runs up into the hook's hairline
    ball = drop(cx - rx + rb + 4, cy + 30, rb, angle=-40, length=rb * 2.3)
    # Bowl: a wide ellipse whose top runs off on a pen-angle tangent into
    # the stem. The counter is narrow and climbs into the stem more steeply,
    # so the diagonal is a hairline at the stem and swells to the left.
    rx, ry = 150, 140
    cx, cy = xs - 110, ry - OV
    xj = xs + STEM / 2
    x0, x1, y0 = cx - rx + STEM * 1.04, xs + 2, -OV + O_THIN
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


def _s(C, top, rx, ry, W, left, right, hair, beak, fall=math.radians(36)):
    """Two elliptical bowls joined by a straight spine: each bowl's outer
    ellipse touches one edge of the spine and its counter the other, so
    every edge runs on smoothly. The lower half is the upper turned 180°
    around C. W is the spine weight measured across; left/right are the
    upper bowl's side weights; beak is the terminal slab's width."""
    n = (math.sin(fall), math.cos(fall))
    nC = n[0] * C[0] + n[1] * C[1]
    cy = top - ry
    s_o = math.hypot(rx * n[0], ry * n[1])
    cx = (nC - W / 2 + s_o - n[1] * cy) / n[0]
    t_o = tangent(cx, cy, rx, ry, (-n[0], -n[1]))[0]
    # Counter: a hairline top, heavy left side, lighter right side.
    rxi, cxi = rx - (left + right) / 2, cx + (left - right) / 2
    top_i = top - hair
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
    upper.cut(Glyph().add(half_plane(t_i, t_o)).clip(rect(-1000, -1000, 2000, cy)))
    # Beak: the terminal thickens into a slab with a flat outer face, its
    # foot cut on the pen angle.
    xe, yc = cx + rx * 0.94, cy - ry * 0.04
    upper.add(Glyph().add(pen_side(xe - beak, xe, xe, yc)).clip(ellipse(cx, cy, rx, ry)))
    upper.cut(pen_side(cx + 20, cx + rx + 40, xe, yc, above=False), rect(xe, yc - 400, xe + 100, cy + ry))
    turn = lambda p: (2 * C[0] - p[0], 2 * C[1] - p[1])
    spine = contour(t_o, turn(t_i), turn(t_o), t_i)
    return Glyph().add(upper, upper.turn(*C), spine)


@glyph("s", 0x73, SB_ROUND, SB_ROUND)
def s():
    return _s((190, XH / 2), XH + OV, 168, 136, 98, 92, 34, THIN + 2, 40)


@glyph("g", 0x67, SB_ROUND, SB_ROUND - 10)
def g():
    ry = 168
    cy = XH + OV - ry
    upper = ring(172, cy, 156, ry, 156 - STEM * 0.9)
    # Ear: a pen-angle bar off the bowl's shoulder, swelling at its tip.
    ear = pen_bar(285, 400, XH - 22, THIN, pivot=285, flare=(0, BAR_TIP * 0.6),
                  flare_len=60, ext=(40, 0))
    # Lower loop: a ring heavy on the right, joined by a straight hairline.
    top, bot = 74, DESC - OV
    ryl = (top - bot) / 2
    loop = ring(228, top - ryl, 214, ryl, 214 - STEM * 0.72, dx_in=-STEM * 0.28)
    link = flared_diag((146, cy - ry + 10), (120, 40), THIN, 34)
    return Glyph().add(upper, ear, link, loop)


# ------------------------------------------------- lowercase: straight diagonals

DIAG = STEM * 1.1     # thick diagonal, measured horizontally
DIAG_HAIR = HAIR * 2 + 6  # thin diagonal
FLARE = 40                # thin diagonals swell by this much into their serifs
FLARE_LEN = 150           # over this much of their height (scaled up for capitals)


def _diag_serif(x0, x1, scale=1.0, cap=False):
    """Foot serif for a diagonal's end, lowercase or capital sized."""
    if cap:
        return foot_serif(x0, x1, reach=CAP_SERIF * scale, tip=CAP_SERIF_TIP, bracket=CAP_BRACKET)
    return foot_serif(x0, x1, reach=SERIF * scale)


def _v(x0, span=430, apex=0.52, left_serif=True, right_serif=True, bottom=None, hair=DIAG_HAIR,
       top=XH, thick=DIAG, cap=False, flare=0):
    """A v from a thick left and a thin right diagonal meeting in a point.
    flare swells the thin diagonal toward its serifed top."""
    xa = x0 + thick / 2
    xb = x0 + span - hair / 2
    xv = x0 + span * apex
    yv = -OV * 1.6 if bottom is None else bottom
    A, B = (xa - thick / 2, top), (xa + thick / 2, top)
    D, E = (xb - hair / 2, top), (xb + hair / 2, top)
    V = (xv, yv)
    C = intersect(B, (B[0] + V[0] - A[0], B[1] + V[1] - A[1]),
                  D, (D[0] + V[0] - E[0], D[1] + V[1] - E[1]))
    g = Glyph().add(contour(A, V, E, D, C, B))
    if flare and right_serif:
        top_mid = ((D[0] + E[0]) / 2, top)
        g.add(flared_stroke(top_mid, (top_mid[0] + (V[0] - E[0]) * 0.6, top + (V[1] - top) * 0.6),
                            hair, flare0=flare, flare_len=FLARE_LEN * top / XH))
    if left_serif:
        g.add(_diag_serif(A[0], B[0], 1.0, cap).mirror_y(top / 2))
    if right_serif:
        g.add(_diag_serif(D[0] - flare / 2, E[0] + flare / 2, 0.8, cap).mirror_y(top / 2))
    return g, V, E


@glyph("v", 0x76, SB_STRAIGHT - 4, SB_STRAIGHT - 4)
def v():
    return _v(0, flare=FLARE)[0]


@glyph("w", 0x77, SB_STRAIGHT - 4, SB_STRAIGHT - 4)
def w():
    first, _, _ = _v(0, span=380, right_serif=False)
    offset = 380 - DIAG_HAIR / 2 - DIAG / 2  # second thick starts on the first thin
    second, _, _ = _v(offset, span=380, flare=FLARE)
    return Glyph().add(first, second)


@glyph("y", 0x79, SB_STRAIGHT - 4, SB_STRAIGHT - 4)
def y():
    span = 430
    hair = DIAG_HAIR
    body, V, E = _v(0, span=span, bottom=-OV, hair=hair, flare=FLARE)
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
    thin = flared_stroke((DIAG_HAIR / 2 + 12, 0), (wd - DIAG_HAIR / 2 - 12, XH), DIAG_HAIR,
                         FLARE, FLARE, FLARE_LEN)
    t0, t1 = 4, DIAG + 4
    h0, h1 = wd - DIAG_HAIR - 12, wd - 12
    return Glyph().add(
        thick, thin,
        foot_serif(t0, t1, reach=SERIF).mirror_y(XH / 2),
        foot_serif(h0 - FLARE / 2, h1 + FLARE / 2, reach=SERIF * 0.8).mirror_y(XH / 2),
        foot_serif(12 - FLARE / 2, 12 + DIAG_HAIR + FLARE / 2, reach=SERIF * 0.8),
        foot_serif(wd - DIAG - 4, wd - 4, reach=SERIF),
    )


@glyph("k", 0x6B, SB_STRAIGHT, SB_STRAIGHT - 6)
def k():
    arm_top = STEM + 250
    arm = flared_stroke((STEM - 10, XH * 0.22), (arm_top, XH), DIAG_HAIR, 0, FLARE, FLARE_LEN)
    # The leg grows out of the arm: trim it along the arm's left edge.
    l1 = (arm_top - DIAG_HAIR / 2, XH)
    l2 = (STEM - 10 - DIAG_HAIR / 2, XH * 0.22)
    below_arm = contour(l2, l1, (l1[0] + 1000, l1[1]), (l1[0] + 1000, -500), (l2[0], -500))
    leg = Glyph().add(diag((STEM + 60, XH * 0.70), (STEM + 262, 0), DIAG)).clip(below_arm)
    right_of_stem = rect(STEM - 2, -50, 900, XH + 50)
    return Glyph().add(
        _stem(0, 0, ASC),
        Glyph().add(arm, leg).clip(right_of_stem),
        foot_serif(arm_top - (DIAG_HAIR + FLARE) / 2, arm_top + (DIAG_HAIR + FLARE) / 2,
                   reach=SERIF * 0.9).mirror_y(XH / 2),
        foot_serif(STEM + 262 - DIAG / 2, STEM + 262 + DIAG / 2, reach=SERIF),
    )


@glyph("z", 0x7A, SB_STRAIGHT, SB_STRAIGHT)
def z():
    wd = 400
    bar = THIN + 5
    slant = STEM * 1.16  # the thick diagonal, measured horizontally
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


ARM = CAP_THIN + 2  # horizontal arms of E F L T Z


@glyph("H", 0x48, CAP_SB_STRAIGHT, CAP_SB_STRAIGHT)
def H():
    w = 590
    bar = CAP * 0.49
    return Glyph().add(
        _cap_stem(0), _cap_stem(w - CAP_STEM),
        pen_bar(CAP_STEM, w - CAP_STEM, bar, CAP_THIN, ext=(CAP_STEM / 2, CAP_STEM / 2)),
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
        pen_bar(CAP_STEM, mid_w, mid0, CAP_THIN, pivot=(CAP_STEM + mid_w) / 2,
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
    return ring(rx, CAP / 2, rx, ry, rx - CAP_STEM * 1.02, thin=CAP_THIN)


CAP_DIAG = CAP_STEM * 1.12      # thick capital diagonal, measured horizontally
CAP_THIN_STEM = CAP_HAIR * 2 + 4  # thin capital stems and diagonals
CAP_BOWL_THIN = CAP_THIN          # thinnest point of capital bowls
CAP_FLARE = 50                    # thin capital strokes swell by this much into their serifs


def _thin_stem(x0, top=CAP, bottom=0, head_left=True, head_right=True, foot=True,
               flare_top=False, flare_foot=False):
    """Thin capital stem; flare_top / flare_foot swell it into its serifs."""
    x1 = x0 + CAP_THIN_STEM
    xm = (x0 + x1) / 2
    reach = CAP_SERIF * 0.85
    f0 = CAP_FLARE if flare_foot else 0
    f1 = CAP_FLARE if flare_top else 0
    g = Glyph().add(flared_stroke((xm, bottom), (xm, top), CAP_THIN_STEM, f0, f1))
    if head_left or head_right:
        g.add(foot_serif(x0 - f1 / 2, x1 + f1 / 2, 0, reach, CAP_SERIF_TIP, CAP_BRACKET,
                         head_left, head_right).mirror_y(CAP / 2))
    if foot:
        g.add(foot_serif(x0 - f0 / 2, x1 + f0 / 2, 0, reach, CAP_SERIF_TIP, CAP_BRACKET))
    return g


def _line_x(p, q, y):
    """x where line p-q crosses height y."""
    return p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1])


def _cap_bowl(x_in, y0, y1, xc, rx, side, t_top=CAP_BOWL_THIN, t_bot=CAP_BOWL_THIN):
    """Bowl of D P R B: flat hairline arms from the stem out to xc, then a
    half ellipse whose far side is `side` thick. The counter's straight
    edges meet its ellipse tangentially, so the arms run smoothly into the
    curve. x_in is the stem's inner edge."""
    cy, ry = (y0 + y1) / 2, (y1 - y0) / 2
    cyi, ryi = (y0 + t_bot + y1 - t_top) / 2, (y1 - t_top - y0 - t_bot) / 2
    return Glyph().add(rect(x_in - 10, y0, xc, y1), ellipse(xc, cy, rx, ry)).cut(
        rect(x_in, y0 + t_bot, xc, y1 - t_top), ellipse(xc, cyi, rx - side, ryi)).clip(
        rect(x_in - 10, y0 - 10, xc + rx + 10, y1 + 10))


@glyph("N", 0x4E, CAP_SB_STRAIGHT - 4, CAP_SB_STRAIGHT - 4)
def N():
    w = 630
    # The thick diagonal leaves the top-left corner and ends in a point on
    # the baseline at the far right.
    rise = (CAP + CAP_OV) / w
    diag_ = contour((0, CAP), (w, -CAP_OV), (w, -CAP_OV + CAP_DIAG * rise), (CAP_DIAG, CAP))
    y_r = -CAP_OV + CAP_THIN_STEM * rise  # where the right stem meets the diagonal's underside
    return Glyph().add(
        _thin_stem(0, head_right=False, flare_foot=True), diag_,
        _thin_stem(w - CAP_THIN_STEM, bottom=y_r, foot=False, flare_top=True),
    )


@glyph("M", 0x4D, CAP_SB_STRAIGHT - 4, CAP_SB_STRAIGHT)
def M():
    w = 800
    xs = w - CAP_STEM
    A, B = (0, CAP), (CAP_DIAG, CAP)
    V = (w * 0.47, -CAP_OV)
    E, D = (xs, CAP), (xs - CAP_THIN_STEM, CAP)
    C = intersect(B, (B[0] + V[0] - A[0], B[1] + V[1] - A[1]),
                  D, (D[0] + V[0] - E[0], D[1] + V[1] - E[1]))
    return Glyph().add(
        _thin_stem(0, head_right=False, flare_foot=True), contour(A, V, E, D, C, B),
        _cap_stem(xs, head_left=False),
    )


def _cap_v(x0, span, **kw):
    return _v(x0, span=span, top=CAP, thick=CAP_DIAG, hair=CAP_THIN_STEM, cap=True,
              **{"apex": 0.5, "bottom": -CAP_OV * 1.6, "flare": CAP_FLARE, **kw})


@glyph("V", 0x56, CAP_SB_STRAIGHT - 22, CAP_SB_STRAIGHT - 22)
def V():
    return _cap_v(0, 650)[0]


@glyph("W", 0x57, CAP_SB_STRAIGHT - 22, CAP_SB_STRAIGHT - 22)
def W():
    span = 500
    first = _cap_v(0, span, right_serif=False)[0]
    second = _cap_v(span - CAP_THIN_STEM / 2 - CAP_DIAG / 2, span)[0]
    return Glyph().add(first, second)


@glyph("A", 0x41, CAP_SB_STRAIGHT - 22, CAP_SB_STRAIGHT - 22)
def A():
    span = 660
    # An upside-down V: thin left, thick right, a sharp apex.
    v_, Vp, E = _cap_v(0, span, bottom=-CAP_OV * 2)
    c = (span / 2, CAP / 2)
    g = v_.turn(*c)
    turn = lambda p: (2 * c[0] - p[0], 2 * c[1] - p[1])
    apex, out_l, out_r = turn(Vp), turn(E), turn((0, CAP))
    # Crossbar rising at the pen angle, flaring where it meets each leg,
    # kept inside the letter's outline.
    yb = CAP * 0.29
    x0 = _line_x(apex, out_l, yb) + CAP_THIN_STEM
    x1 = _line_x(apex, out_r, yb) - CAP_DIAG
    bar = Glyph().add(pen_bar(x0, x1, yb, CAP_THIN, flare=(BAR_FLARE * 0.25, BAR_TIP * 0.6),
                              flare_len=70, ext=(60, 60)))
    return g.add(bar.clip(contour(apex, out_r, out_l)))


@glyph("X", 0x58, CAP_SB_STRAIGHT - 20, CAP_SB_STRAIGHT - 20)
def X():
    wd = 640
    t0, t1 = 6, CAP_DIAG + 6
    h0, h1 = wd - CAP_THIN_STEM - 16, wd - 16
    return Glyph().add(
        diag((CAP_DIAG / 2 + 6, CAP), (wd - CAP_DIAG / 2 - 6, 0), CAP_DIAG),
        flared_stroke((CAP_THIN_STEM / 2 + 16, 0), (wd - CAP_THIN_STEM / 2 - 16, CAP), CAP_THIN_STEM,
                      CAP_FLARE, CAP_FLARE),
        _diag_serif(t0, t1, cap=True).mirror_y(CAP / 2),
        _diag_serif(h0 - CAP_FLARE / 2, h1 + CAP_FLARE / 2, 0.8, cap=True).mirror_y(CAP / 2),
        _diag_serif(16 - CAP_FLARE / 2, 16 + CAP_THIN_STEM + CAP_FLARE / 2, 0.8, cap=True),
        _diag_serif(wd - CAP_DIAG - 6, wd - 6, cap=True),
    )


@glyph("Y", 0x59, CAP_SB_STRAIGHT - 20, CAP_SB_STRAIGHT - 20)
def Y():
    arms, Vp, _ = _cap_v(0, 640, bottom=CAP * 0.36)
    s0 = Vp[0] - CAP_STEM / 2
    return Glyph().add(arms, rect(s0, 0, s0 + CAP_STEM, CAP * 0.44), cap_foot(s0, s0 + CAP_STEM))


@glyph("K", 0x4B, CAP_SB_STRAIGHT, CAP_SB_STRAIGHT - 16)
def K():
    arm_top = CAP_STEM + 380
    low = (CAP_STEM - 10, CAP * 0.26)
    arm = flared_stroke(low, (arm_top, CAP), CAP_THIN_STEM, 0, CAP_FLARE)
    # The leg grows out of the arm: trim it along the arm's left edge.
    l1 = (arm_top - CAP_THIN_STEM / 2, CAP)
    l2 = (low[0] - CAP_THIN_STEM / 2, low[1])
    below_arm = contour(l2, l1, (l1[0] + 1000, l1[1]), (l1[0] + 1000, -500), (l2[0], -500))
    foot_x = CAP_STEM + 420
    leg = Glyph().add(diag((CAP_STEM + 110, CAP * 0.62), (foot_x, 0), CAP_DIAG)).clip(below_arm)
    return Glyph().add(
        _cap_stem(0),
        Glyph().add(arm, leg).clip(rect(CAP_STEM - 2, -50, 1200, CAP + 50)),
        _diag_serif(arm_top - (CAP_THIN_STEM + CAP_FLARE) / 2, arm_top + (CAP_THIN_STEM + CAP_FLARE) / 2, 0.9,
                    cap=True).mirror_y(CAP / 2),
        _diag_serif(foot_x - CAP_DIAG / 2, foot_x + CAP_DIAG / 2, cap=True),
    )


@glyph("Z", 0x5A, CAP_SB_STRAIGHT - 6, CAP_SB_STRAIGHT - 6)
def Z():
    wd = 560
    bar = ARM + 2
    slant = CAP_STEM * 1.16
    return Glyph().add(
        rect(0, CAP - bar, wd, CAP),
        contour((wd - slant, CAP - bar), (wd, CAP - bar), (slant, bar), (0, bar)),
        rect(0, 0, wd, bar),
        arm_serif(wd, 0, bar, 150).mirror_x(wd / 2).mirror_y(CAP / 2),
        arm_serif(wd, 0, bar, 170),
    )


def _c_ring(rx):
    ry = CAP / 2 + CAP_OV
    return rx, ry, ring(rx, CAP / 2, rx, ry, rx - CAP_STEM * 0.95, thin=CAP_BOWL_THIN, dx_in=18)


def _beak(g, cx, rx, ry, yc, width=48):
    """Top terminal of C, G: the stroke thickens into a slab with a flat
    outer face, its foot cut on the pen angle."""
    xe = cx + rx * 0.93
    g.add(Glyph().add(pen_side(xe - width, xe, xe, yc)).clip(ellipse(cx, CAP / 2, rx, ry)))
    g.cut(rect(xe, yc, xe + 200, CAP + 100))
    return xe


@glyph("C", 0x43, CAP_SB_ROUND, CAP_SB_ROUND - 14)
def C():
    rx, ry, g = _c_ring(322)
    cx = rx
    yt, yb = CAP * 0.64, CAP * 0.26
    xe = _beak(g, cx, rx, ry, yt)
    # Aperture between the beak's pen-cut foot and the lower terminal's
    # pen-cut end.
    g.cut(Glyph().add(pen_side(cx + 20, cx + rx + 60, xe, yt, above=False))
          .clip(pen_side(cx + 20, cx + rx + 60, cx + rx, yb)))
    return g


@glyph("G", 0x47, CAP_SB_ROUND, CAP_SB_STRAIGHT - 6)
def G():
    rx, ry, g = _c_ring(330)
    cx = rx
    yt = CAP * 0.64
    xe = _beak(g, cx, rx, ry, yt)
    # A short stem whose outer edge carries on straight down from the
    # bowl's widest point, with a spur at the foot. Its head is the u's
    # wedge: the top runs straight up the pen angle from the tip to the
    # stem's corner, and the underside sweeps down onto the bowl's inner
    # edge where it meets the stem.
    xs1 = cx + rx
    xs0 = xs1 - CAP_STEM
    y_ink = next(y for y in range(0, 400) if g.path.contains((xs0 - 2, y)))  # bowl's outer edge
    y_join = next(y for y in range(y_ink, 400) if not g.path.contains((xs0 - 2, y)))  # its inner edge
    reach = 84
    tip = (xs0 - reach, y_join + 74)
    yg = tip[1] + (CAP_STEM + reach) * math.tan(PEN)
    g.cut(Glyph().add(pen_side(cx + 20, cx + rx + 60, xe, yt, above=False))
          .clip(rect(cx + 20, yg - 40, cx + rx + 60, CAP)))
    head = contour(
        (xs1, yg), tip, (tip[0], tip[1] - CAP_SERIF_TIP),
        ((xs0 - reach * 0.5, tip[1] - 14), (xs0 - 6, tip[1] - 40), (xs0, y_join - 6)),
        (xs1, y_join - 6),
    )
    return g.add(rect(xs0, 60, xs1, y_join), head, spur(xs0, xs1, 0))


@glyph("Q", 0x51, CAP_SB_ROUND, -70)  # the tail tucks under the next letter
def Q():
    rx = 364
    ry = CAP / 2 + CAP_OV
    o = ring(rx, CAP / 2, rx, ry, rx - CAP_STEM * 1.02, thin=CAP_THIN)
    # Tail: a crescent between two ellipse arcs, sweeping out from under the
    # bowl and ending on a pen-angle cut.
    cx = rx
    tail = Glyph().add(ellipse(cx + 290, -4, 300, 170)).cut(ellipse(cx + 330, 40, 290, 180))
    tail.clip(rect(cx - 40, -400, cx + rx + 120, 0))
    tail.cut(pen_side(cx + 200, cx + rx + 200, cx + 390, -150, above=False))
    return o.add(tail)


@glyph("U", 0x55, CAP_SB_STRAIGHT - 4, CAP_SB_STRAIGHT - 4)
def U():
    w = 640
    cy = 260
    # Lower half of a ring whose sides leave the two stems straight down:
    # thick on the left, thin on the right.
    rx_in = (w - CAP_THIN_STEM - CAP_STEM) / 2
    bowl_ = ring(w / 2, cy, w / 2, cy + CAP_OV, rx_in, thin=CAP_BOWL_THIN,
                 dx_in=(CAP_STEM - CAP_THIN_STEM) / 2)
    bowl_.clip(rect(-10, -100, w + 10, cy))
    return Glyph().add(
        bowl_,
        rect(0, cy - 1, CAP_STEM, CAP), cap_head(0, CAP_STEM, CAP),
        _thin_stem(w - CAP_THIN_STEM, bottom=cy - 1, foot=False, flare_top=True),
    )


@glyph("J", 0x4A, CAP_SB_ROUND - 10, CAP_SB_STRAIGHT)
def J():
    x0 = 230
    x1 = x0 + CAP_STEM
    rx, cy, left = 210, 168, 60  # a shallow bowl keeps the bottom flat
    cx = x1 - rx
    # Hook: the lower half of a ring leaving the stem straight down, ending
    # on the left in a teardrop, the a's terminal turned upside down.
    hook = ring(cx, cy, rx, cy + CAP_OV, rx - (CAP_STEM + left) / 2, thin=CAP_BOWL_THIN,
                dx_in=(left - CAP_STEM) / 2)
    hook.clip(rect(cx - rx - 10, -100, x1 + 10, cy))
    rb = 54
    # The ball's leftmost point is the ring's, so the outer edge runs on
    # unbroken; the tail hugs the ring's inner edge.
    tear = drop(cx - rx + rb, cy, rb, angle=192, length=rb * 2.6)
    return Glyph().add(hook, tear, rect(x0, cy - 1, x1, CAP), cap_head(x0, x1, CAP))


@glyph("D", 0x44, CAP_SB_STRAIGHT, CAP_SB_ROUND)
def D():
    xc = 290
    return Glyph().add(
        _cap_stem(0, head_right=False, foot_right=False),
        _cap_bowl(CAP_STEM, 0, CAP, xc, 330, CAP_STEM * 1.04),
    )


@glyph("P", 0x50, CAP_SB_STRAIGHT, CAP_SB_ROUND - 10)
def P():
    yb = CAP * 0.40
    return Glyph().add(
        _cap_stem(0, head_right=False),
        _cap_bowl(CAP_STEM, yb, CAP, 250, 230, CAP_STEM * 0.98, t_bot=CAP_BOWL_THIN + 4),
    )


@glyph("R", 0x52, CAP_SB_STRAIGHT, CAP_SB_STRAIGHT - 20)
def R():
    yb = CAP * 0.42
    t_bot = CAP_BOWL_THIN + 4
    xc, rx = 240, 225
    # Leg: a thick diagonal from the bowl's underside to a serifed foot.
    foot_x = xc + rx + 30
    leg = Glyph().add(diag((xc - 10, yb + 60), (foot_x, 0), CAP_DIAG)).clip(
        rect(CAP_STEM, -10, 1000, yb + t_bot))
    return Glyph().add(
        _cap_stem(0, head_right=False),
        _cap_bowl(CAP_STEM, yb, CAP, xc, rx, CAP_STEM * 0.98, t_bot=t_bot),
        leg, _diag_serif(foot_x - CAP_DIAG / 2, foot_x + CAP_DIAG / 2, cap=True),
    )


@glyph("B", 0x42, CAP_SB_STRAIGHT, CAP_SB_ROUND - 6)
def B():
    ym = CAP * 0.53  # bottom of the middle arm
    tm = CAP_BOWL_THIN + 4
    return Glyph().add(
        _cap_stem(0, head_right=False, foot_right=False),
        _cap_bowl(CAP_STEM, ym, CAP, 230, 200, CAP_STEM * 0.9, t_bot=tm),
        _cap_bowl(CAP_STEM, 0, ym + tm, 250, 236, CAP_STEM * 1.0, t_top=tm),
    )


@glyph("S", 0x53, CAP_SB_ROUND, CAP_SB_ROUND)
def S():
    return _s((260, CAP / 2), CAP + CAP_OV, 236, 188, 118, 116, 40, CAP_THIN + 2, 50)


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
