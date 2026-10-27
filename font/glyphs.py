"""Glyph definitions. Each function draws one letter from shared parts;
the build script places it between its sidebearings."""
import math

from .draw import Glyph, contour, ellipse, rect
from .params import (ARCH_THIN, ASC, BAR_FLARE, BAR_TIP, CAP, CAP_HAIR, CAP_OV, CAP_SB_ROUND, CAP_SERIF_TIP,
                     CAP_SB_STRAIGHT, CAP_STEM, DESC, HAIR, M_COUNTER,
                     K_OUT, N_COUNTER, O_THIN, OV, PEN, SB_ROUND, SB_STRAIGHT, SERIF, SPACE, STEM,
                     XH)
from .parts import (arch, bowl, cap_foot, cap_head, foot_serif, head_serif,
                    nib_dot, pen_bar, ring, spur)

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
    bar = Glyph().add(pen_bar(x_in, x_out, bar0, HAIR + 2, pivot=cx,
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
