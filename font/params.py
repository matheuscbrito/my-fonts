"""Shared design parameters. Every glyph is built from these numbers,
so changing one here changes the whole typeface.

Units are font units on a 1000-unit em.
"""
import math

FAMILY = "Senna Display"  # the typeface name, rename any time
STYLE = "Regular"
VERSION = "0.4"
UPM = 1000

# Vertical metrics
CAP = 640          # cap height
XH = 444           # x-height (large, for headline legibility)
ASC = 700          # lowercase ascenders rise above caps, an elegant touch
DESC = -210
OV = 11            # overshoot of round lowercase shapes
CAP_OV = 13        # overshoot of round capitals

# Stroke contrast: heavy stems against needle-thin hairlines, very high
STEM = 106         # lowercase vertical stem
CAP_STEM = 114     # capital vertical stem
HAIR = 9           # lowercase hairline (serif tips and fine details)
CAP_HAIR = 10      # capital hairline
# The thin strokes that carry a letter, kept even across the alphabet
THIN = 11          # lowercase bars, links, ears, arches and bowls
CAP_THIN = 12      # capital crossbars and the thinnest points of capital bowls
# Curves are drawn heavier than stems, as in the a's bowl, so they read as
# equally dark; their thinnest points and crossbars are a touch firmer than
# THIN, since a long hairline reads lighter than a short one.
ROUND = round(STEM * 1.12)          # widest point of lowercase curves (119)
CAP_ROUND = round(CAP_STEM * 1.1)   # widest point of capital curves (125)
BAR_THIN = THIN + 3                 # lowercase crossbars (e, t, f, z)
CAP_BAR_THIN = CAP_THIN + 3         # capital crossbars and arms

# Serifs (flared diagonal wedges, cut like a broad-nib pen)
HEAD = 92          # lowercase head serif reach to the left
HEAD_SLOPE = 74    # drop of the head serif's top edge
# The pen angle comes from the head wedge; foot serifs and spurs reuse it,
# so every diagonal in the face shares one slope (about 20 degrees).
PEN = math.atan2(HEAD_SLOPE, STEM + HEAD)
SERIF = 56         # lowercase foot serif reach beyond the stem
SERIF_TIP = 4      # thickness at the serif's tip
BRACKET = round(SERIF_TIP + SERIF * math.tan(PEN) * 1.15)  # flank height at the stem
CAP_SERIF = 64
CAP_SERIF_TIP = 5
CAP_BRACKET = round(CAP_SERIF_TIP + CAP_SERIF * math.tan(PEN) * 1.15)
# Crossbars rise at the pen angle and swell toward their ends
BAR_FLARE = 44     # extra thickness at the left end of a bar
BAR_TIP = 88       # extra thickness at the right tip, the expressive end
BAR_FLARE_LEN = 150  # how far in from the end the swelling starts

# Arches (n, m, h, u)
ARCH_THIN = THIN   # thickness at the top of the arch
N_COUNTER = 230    # white space inside n
M_COUNTER = 198    # white space inside each half of m

# Round shapes
O_THIN = THIN + 2  # thinnest point of bowls, the a's crown
STRESS = 0         # tilt of the stress axis in degrees (0 = vertical, negative leans right)
# Curve fullness: 0.5523 is a true ellipse; higher flattens the sides and
# hardens the corners toward a superellipse.
K_OUT = 0.76       # outer contours of bowls and rings
K_IN = 0.73        # counters, a touch rounder so the thin points stay crisp
ARCH_K = 0.84      # shoulder fullness of n m h u arches (0.56 = soft)

# Spacing, measured from the outermost ink (serif tips included)
SB_STRAIGHT = 20
SB_ROUND = 30
CAP_SB_STRAIGHT = 26
CAP_SB_ROUND = 38
SPACE = 220
