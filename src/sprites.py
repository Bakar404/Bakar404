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
BOT_SWEATING = (  # a drop on its head, a wobbly mouth
    ["...........#....", ".......##.#p#..."] + _BOT_TOP[2:] + _BOT_EYES
    + ["..#pppppppppp#..", "..#pp#p#p#p#p#..", "..#p#p#p#p#pp#.."] + _BOT_BOTTOM[3:]
)
BOT_ANTENNA_ROWS = 2  # rows 0-1: the antenna, animated separately

# A match for the Nim heaps: yellow head, ink stick.
MATCH = [
    ".##.",
    "#YY#",
    "#YY#",
    "#YY#",
    ".##.",
] + [".##."] * 7

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

# Ahmed, waving, after the character from my game: curly black hair worn up, glasses, a full black
# beard, a blue sweater, dark trousers, brown shoes.
# Unlike the 1-bit art it keeps its colours in both themes; only the outline ('o') follows the
# theme, which gives it a sticker edge on dark backgrounds. The raised arm lives in the two wave
# frames, drawn over the empty columns on the left.
AVATAR = [
    "..............o........",
    "............ooAoo......",
    "..........ooABABAoo....",
    ".........oAACDADBBAo...",
    ".........oEDCAEECCAo...",
    "........oACACCADCAAAo..",
    ".......oAACBDCADDBDAAo.",
    ".......oADDABBADDBDAAo.",
    ".......oAAAFGGEGIJAAAo.",
    ".......oAAEKIGLGIMAAAo.",
    "........oNEEOPIQOOERo..",
    "........oNABSFOBTDARo..",
    ".........oAUUUNUUCAo...",
    ".........oAAYGNGaAAo...",
    ".........oABDCCCDBAo...",
    ".........oAABlllBAAo...",
    ".........oAABBDBBAAo...",
    "........ofgjABDBAjgfo..",
    "........ofjiifffiijfo..",
    ".........ofgiiiiigfjho.",
    ".........ofgiiiiigfiho.",
    ".........ofgiiiiigfgho.",
    ".........ofgiiiiigfgho.",
    ".........ofggggggffgiho",
    ".........ofggggggffgjho",
    ".........ofggggggffgjho",
    ".........ofggggggffecOo",
    ".........oAAAAAAAAAcReo",
    ".........oADDDDDDDAcReo",
    ".........oADDBBEDDBEMeo",
    "........oADDCAAEDDDEoo.",
    "........oADDCEoADDDEo..",
    "........oEDDEooADDDAo..",
    "........oEDDEo.oABDAo..",
    "........oECDEo.oACkAo..",
    "........oAAAEo.oABBAo..",
    ".......oOJcdOo.oAFeeOo.",
    ".......oOJcFOo..oFeJOo.",
    ".......oOdXPOo..oFXQFo.",
    "........oOOOo...oOOOo..",
    ".........ooo.....ooo...",
]
_HAND_LEFT = [
    "...ooo....",
    "..oGGGo...",
    "..oGIGo...",
    "..oGGGKo..",
    "..oMGMo...",
    "...ohjo...",
    "...ofjo...",
    "...ofjo...",
    "...ofjio..",
    "....ofjio.",
    ".....ofjij",
    "......ofji",
    ".......oo.",
]
_HAND_RIGHT = [
    ".ooo......",
    "oGGGo.....",
    "oGIGo.....",
    "oGGGKo....",
    ".oMGMo....",
    "..ohjo....",
    "..ofjo....",
    "...ofjo...",
    "...ofjio..",
    "....ofjio.",
    ".....ofjij",
    "......ofji",
    ".......oo.",
]
AVATAR_HANDS = (_HAND_LEFT, _HAND_RIGHT)
AVATAR_HAND_AT = (0, 7)
AVATAR_MOUTH = 15  # the row a speech tail aims at
# Drawn over closed eyes, so hiding them for a moment is a blink.
AVATAR_EYES = [(12, 12), (16, 12)]
AVATAR_COLOURS = {  # sprite char: (CSS class, colour)
    # one dark ramp for hair, beard and trousers
    "E": ("dark0", "#1c141b"), "A": ("dark1", "#211a25"), "B": ("dark2", "#2f2a36"),
    "D": ("dark3", "#3e3945"), "C": ("dark4", "#4b4753"), "k": ("dark5", "#625053"),
    # one warm ramp for skin, brows, lips and shoes
    "N": ("warm0", "#faebdb"), "R": ("warm1", "#f9dfc8"), "I": ("warm2", "#fad2b7"),
    "G": ("warm3", "#f9c29d"), "L": ("warm4", "#dfb3a4"), "X": ("warm5", "#da7f62"),
    "K": ("warm6", "#d16d4b"), "Q": ("warm7", "#c6876b"), "P": ("warm8", "#c2755b"),
    "M": ("warm9", "#bd5f41"), "c": ("warm10", "#a86850"), "l": ("warm11", "#a5483b"),
    "e": ("warm12", "#a2533b"), "J": ("warm13", "#8c5243"), "d": ("warm14", "#86412e"),
    "F": ("warm15", "#5f3430"), "O": ("warm16", "#462828"),
    # glasses
    "U": ("frame0", "#282d51"), "Y": ("frame1", "#666069"), "a": ("frame2", "#9a8e98"),
    "S": ("lens0", "#c4b9c4"), "T": ("lens1", "#aab3ca"), "V": ("eyes", "#f7fafd"),
    # the sweater
    "h": ("blue0", "#12315c"), "f": ("blue1", "#303d6b"), "g": ("blue2", "#364c85"),
    "i": ("blue3", "#42619c"), "j": ("blue4", "#4c6ead"),
}
AVATAR_PALETTE = {"o": "i", **{ch: cls for ch, (cls, _) in AVATAR_COLOURS.items()}}
AVATAR_CSS = "".join(sorted({f".{cls}{{fill:{colour}}}" for cls, colour in AVATAR_COLOURS.values()}))


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
    "human": HUMAN, "bot": BOT, "bot_sweating": BOT_SWEATING, "match": MATCH,
    "pen_nib": PEN_NIB, "chip": CHIP, "toggles": TOGGLES, "matrix": MATRIX,
}
