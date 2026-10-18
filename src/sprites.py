"""Hand-drawn 1-bit sprites.

Legend: '#' ink, 'p' panel (opaque fill), 'Y' accent, 'k' ink-on-accent,
'd' dither, '.' transparent.
"""
from __future__ import annotations

PALETTE = {"#": "i", "p": "p", "Y": "a", "k": "k", "d": "d", "m": "m"}

# The visitor. Yellow is reserved for "you" and for things you can press.
HUMAN = [
    "................",
    ".....######.....",
    "....########....",
    "...##########...",
    "...##pppppp##...",
    "...#pppppppp#...",
    "..##pp#pp#pp##..",
    "..##pppppppp##..",
    "...#ppp##ppp#...",
    "....#pppppp#....",
    ".....######.....",
    "....#YY##YY#....",
    "..##YYY##YYY##..",
    ".#YYYYYYYYYYYY#.",
    ".#YYYYYYYYYYYY#.",
    ".##############.",
]

_BOT_TOP = [
    ".......##.......",
    ".......##.......",
    "..############..",
    "..#pppppppppp#..",
]
_BOT_EYES = [
    ".##pp##pp##pp##.",
    ".##pp##pp##pp##.",
]
_BOT_EYES_SUSPICIOUS = [
    ".##ppp#pp#ppp##.",
    ".##pp##pp##pp##.",
]
_BOT_BOTTOM = [
    "..#pppppppppp#..",
    "..#pp######pp#..",
    "..#pppppppppp#..",
    "..############..",
    "......####......",
    "..############..",
    ".#pppppppppppp#.",
    ".#ppp######ppp#.",
    ".#pppppppppppp#.",
    ".##############.",
]
BOT = _BOT_TOP + _BOT_EYES + _BOT_BOTTOM
BOT_SUSPICIOUS = (
    _BOT_TOP[:3] + ["..#p##pppp##p#.."] + _BOT_EYES_SUSPICIOUS
    + ["..#pppppppppp#..", "..#pppp####pp#.."] + _BOT_BOTTOM[2:]
)
BOT_ANTENNA_ROWS = 2  # rows 0-1: the antenna, animated separately

PEN_NIB = [
    "....########....",
    "....#pppppp#....",
    "...##########...",
    "..#pppppppppp#..",
    "..#pppppppppp#..",
    "..#ppp####ppp#..",
    "..#ppp#..#ppp#..",
    "..#ppp####ppp#..",
    "...#ppp##ppp#...",
    "...#ppp##ppp#...",
    "....#pp##pp#....",
    "....#pp##pp#....",
    ".....#p##p#.....",
    ".....#p##p#.....",
    "......####......",
    ".......##.......",
]

# Feature flags: one switched on, one off.
TOGGLES = [
    "..###########..",
    ".#############.",
    "#########ppp###",
    "#########ppp###",
    "#########ppp###",
    ".#############.",
    "..###########..",
    "...............",
    "..###########..",
    ".#ppppppppppp#.",
    "#pp###pppppppp#",
    "#pp###pppppppp#",
    "#pp###pppppppp#",
    ".#ppppppppppp#.",
    "..###########..",
]

# A chip with "AI" on its die.
CHIP = [
    "....#..#..#....",
    "....#..#..#....",
    "..###########..",
    "..#ppppppppp#..",
    "###ppppppppp###",
    "..#pp#pp###p#..",
    "..#p#p#pp#pp#..",
    "###p###pp#pp###",
    "..#p#p#pp#pp#..",
    "..#p#p#p###p#..",
    "###ppppppppp###",
    "..#ppppppppp#..",
    "..###########..",
    "....#..#..#....",
    "....#..#..#....",
]

# A payoff matrix: the cooperative cell is dithered, the equilibrium is solid.
MATRIX = [
    "###############",
    "#dddddd#......#",
    "#dddddd#......#",
    "#dddddd#......#",
    "#dddddd#......#",
    "#dddddd#......#",
    "#dddddd#......#",
    "###############",
    "#......########",
    "#......########",
    "#......########",
    "#......########",
    "#......########",
    "#......########",
    "###############",
]

# Selected frames for the interests menu, shown one at a time like a game's attract mode.
def _swap(rows: list[str], x0: int, y0: int, x1: int, y1: int) -> list[str]:
    """Swap ink and panel inside a box, the way a 1-bit UI shows a selection."""
    flip = {"#": "p", "p": "#"}
    return [row[:x0] + "".join(flip.get(ch, ch) for ch in row[x0:x1 + 1]) + row[x1 + 1:]
            if y0 <= y <= y1 else row for y, row in enumerate(rows)]


PEN_NIB_ON = [  # inked
    "....########....",
    "....#pppppp#....",
    "...##########...",
    "..############..",
    "..############..",
    "..############..",
    "..#####..#####..",
    "..############..",
    "...####pp####...",
    "...####pp####...",
    "....###pp###....",
    "....###pp###....",
    ".....##pp##.....",
    ".....##pp##.....",
    "......####......",
    ".......##.......",
]
CHIP_ON = _swap(CHIP, 3, 3, 11, 11)  # powered on
TOGGLES_ON = TOGGLES[8:] + TOGGLES[7:8] + TOGGLES[:7]  # both flipped
MATRIX_ON = (MATRIX[:1] + ["########......#"] * 6 + MATRIX[7:8]  # cooperation wins
             + ["#......#dddddd#"] * 6 + MATRIX[14:])

ALL = {
    "human": HUMAN, "bot": BOT, "bot_suspicious": BOT_SUSPICIOUS,
    "pen_nib": PEN_NIB, "chip": CHIP, "toggles": TOGGLES, "matrix": MATRIX,
}
