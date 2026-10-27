"""Optical kerning, measured from the outlines.

Each glyph is sliced into horizontal bands, and for each band we record how
far its ink sits from its left and right edges (its sidebearings plus any
open space, such as under the arms of a T). Two glyphs side by side look
evenly spaced when their closest parts sit as close as they would next to
an ordinary letter. So for a pair we compare:

  actual   the closeness of the pair itself: in every band, the space from
           the left glyph's ink to the right glyph's ink, reduced to one
           number by averaging the closest bands;
  expected the same measure for each glyph on its own (its right side and
           the other's left side), as if each sat next to a straight stem.

When open shapes meet (A next to V, T over o, L next to T) the pair's
closest bands don't line up, so the actual space is larger than expected and
the pair is pulled together by part of the difference. Pairs that already
work, like n n or o o, come out at zero. A collision guard keeps every pair
apart over the full height, descenders and tails included.
"""
import pathops

from .params import ASC, CAP, DESC, OV, XH

STEP = 10            # band height
OPEN = 260           # space counted for a band with no ink: open, but not endless
NEAREST = 0.3        # fraction of bands, the closest ones, that set the closeness
STRENGTH = 0.55      # how much of the difference the kern makes up
MIN_GAP = 34         # ink never comes closer than this
LIMIT = (-110, 20)   # range of kerning values
ROUND_TO = 5
SKIP = 10            # values smaller than this are left out

LOWER_ZONE = (0, XH)
CAP_ZONE = (0, CAP)
FULL = (DESC - OV - 60, ASC + OV + 60)


def _zone(name):
    if name in ("period", "comma"):
        return LOWER_ZONE
    return CAP_ZONE if name[0].isupper() else LOWER_ZONE


def _bands(lo, hi):
    return range(int(lo // STEP) * STEP, int(hi), STEP)


def profile(path, width):
    """{band: (space left of the ink, space right of it)}, from the glyph's
    placed outline and advance width."""
    out = {}
    for y in _bands(*FULL):
        band = pathops.Path()
        pen = band.getPen()
        pen.moveTo((-2000, y)); pen.lineTo((3000, y)); pen.lineTo((3000, y + STEP)); pen.lineTo((-2000, y + STEP))
        pen.closePath()
        ink = pathops.op(path, band, pathops.PathOp.INTERSECTION)
        b = ink.bounds
        if b and b[2] > b[0]:
            out[y] = (b[0], width - b[2])
    return out


def _closeness(values):
    values = sorted(values)
    n = max(1, round(len(values) * NEAREST))
    return sum(values[:n]) / n


def _side(prof, zone, side):
    return _closeness([prof[y][side] if y in prof else OPEN for y in _bands(*zone)])


def kern_pair(left, right, profiles, zones):
    pl, pr = profiles[left], profiles[right]
    zone = (0, min(zones[left][1], zones[right][1]))
    actual = _closeness([min((pl[y][1] if y in pl else OPEN) + (pr[y][0] if y in pr else OPEN), 2 * OPEN)
                         for y in _bands(*zone)])
    expected = _side(pl, zones[left], 1) + _side(pr, zones[right], 0)
    k = STRENGTH * (expected - actual)
    k = max(LIMIT[0], min(LIMIT[1], k))
    # Never let the inks come closer than MIN_GAP anywhere.
    shared = [pl[y][1] + pr[y][0] for y in pl if y in pr]
    if shared:
        k = max(k, MIN_GAP - min(shared))
    k = ROUND_TO * round(k / ROUND_TO)
    return k if abs(k) >= SKIP else 0


def feature(placed):
    """placed: {glyph name: (outline in its final position, advance width)}."""
    names = [n for n in placed if n not in ("space", ".notdef")]
    profiles = {n: profile(*placed[n]) for n in names}
    zones = {n: _zone(n) for n in names}
    lines = []
    for l in names:
        for r in names:
            k = kern_pair(l, r, profiles, zones)
            if k:
                lines.append("    pos %s %s %d;" % (l, r, k))
    return "feature kern {\n" + "\n".join(lines) + "\n} kern;\n"
