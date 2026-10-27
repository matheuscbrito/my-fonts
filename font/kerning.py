"""Kerning: pairs of glyph groups and the adjustment between them, in font
units (negative pulls the pair together). The build expands every group pair
into glyph pairs and writes them to the kern feature."""

ROUND_LC = "a c d e g o q s".split()   # lowercase with round left sides
DIAG_LC = "v w y".split()
PUNCT = "period comma".split()
ROUND_UC = "C G O Q".split()

KERN = [
    # A against diagonals and rounds
    (["A"], ["V", "W"], -70), (["A"], ["Y"], -75), (["A"], ["T"], -60),
    (["A"], ROUND_UC + ["U"], -20), (["A"], DIAG_LC, -35),
    (["V", "W"], ["A"], -70), (["Y"], ["A"], -80), (["T"], ["A"], -60),
    (["O", "D", "Q"], ["A"], -22), (["O", "D", "Q"], ["V", "W", "X"], -25),
    (["O", "D", "Q"], ["Y"], -32), (["O", "D", "Q"], ["T"], -15),
    # Overhanging tops over lowercase and punctuation
    (["T"], ROUND_LC, -80), (["T"], ["u", "r", "n", "m"], -55), (["T"], DIAG_LC + ["x", "z"], -55),
    (["T"], PUNCT, -80),
    (["V", "W"], ROUND_LC, -55), (["V", "W"], ["u", "r", "n", "m"], -30), (["V", "W"], PUNCT, -80),
    (["Y"], ROUND_LC, -75), (["Y"], ["u", "n", "m", "r"], -45), (["Y"], PUNCT, -90),
    (["F"], ["A"], -40), (["F"], PUNCT, -80), (["F"], ROUND_LC, -20),
    (["P"], ["A"], -50), (["P"], PUNCT, -100), (["P"], ROUND_LC, -25),
    # Open right sides
    (["L"], ["T"], -80), (["L"], ["V", "W"], -75), (["L"], ["Y"], -85), (["L"], DIAG_LC, -40),
    (["L"], ROUND_UC, -20),
    (["K", "X"], ROUND_UC, -30), (["K"], ROUND_LC, -25),
    (["R"], ["V", "W"], -20), (["R"], ["Y"], -30), (["R"], ["T"], -15),
    # Lowercase
    (["r"], PUNCT, -50), (DIAG_LC, PUNCT, -50), (["f"], PUNCT, -40),
    (["r"], ["a", "c", "d", "e", "o", "q"], -10),
    (["k", "x"], ["a", "c", "d", "e", "o", "q"], -18),
    (DIAG_LC, ["a", "c", "d", "e", "o", "q"], -14),
    (["a", "b", "c", "e", "o", "p"], DIAG_LC + ["x"], -14),
]


def feature():
    pairs = {}
    for lefts, rights, value in KERN:
        for l in lefts:
            for r in rights:
                pairs[(l, r)] = value
    lines = ["    pos %s %s %d;" % (l, r, v) for (l, r), v in sorted(pairs.items())]
    return "feature kern {\n" + "\n".join(lines) + "\n} kern;\n"
