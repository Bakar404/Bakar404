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

# Ahmed, waving: dark hair, glasses, a full beard, a navy blazer over a light-blue shirt.
# Unlike the 1-bit art it keeps its colours in both themes; only the outline ('o') follows the
# theme, which gives it a sticker edge on dark backgrounds.
AVATAR = [
    "......................................",
    "......................ooooooo.........",
    "....................ooHHHHHHHoo.......",
    "...................oHHHhhhHHHHHo......",
    "..................oHHhhHHHHHHHHHo.....",
    ".................oHHhHHHHHHHHHHHo.....",
    ".................oHHHHHHHHHHHHHHo.....",
    ".................oHHHHHHHHHHHHHHo.....",
    ".................oHHSHHSSSSHHSHHo.....",
    ".................oHSSSSSSSSSSSSHo.....",
    ".................oHGGGGGSSGGGGGHo.....",
    "................osSGSsSGGGGSsSGSso....",
    "................osSGSSSGSSGSSSGSso....",
    "................osSSGGGSssSGGGSSso....",
    ".................obSSSSSssSSSSSbo.....",
    ".................obSSSBBBBBBSSSbo.....",
    ".................obbSBMWWWWMBSbbo.....",
    ".................obbbBBBBBBBBbbbo.....",
    "..................obbbBBBBBBbbbo......",
    ".....oNNNNNo.......obbBBBBBBbbo.......",
    ".....oNNNnNo........oxBBBBBBxo........",
    ".....oNNNnNo..........xxxxxx..........",
    ".....oNNNnNo..........oSSSSo..........",
    ".....oNNNnNo....oNNNnTTSSSSTTnNNNo....",
    ".....oNNNnNo..oNNNNNNnTTSSTTnNNNNNNo..",
    ".....oNNNnNo.oNNNNNNNnTTTTTTnNNNNNNNo.",
    ".....oNNNnNooNNNNNNNNnTTTTTTnNNNNNNNNo",
    ".....oNNNnNooNNNNNNNNNnTTTTnNNNNNNNNNo",
    ".....oNNNnNooNNNNNNNNNnTTTTnNNNNNNNNNo",
    ".....oNNNnNooNNNNNNNNNnTTTTnNNNNNNNNNo",
    ".....oNNNnNooNNNNNNNNNnTTTTnNNNNNNNNNo",
    ".....oNNNnNooNNNNNNNNNNnTTnNNNNNNNNNNo",
    ".....oNNNnNooNNNNNNNNNNnTTnNNNNNNNNNNo",
]
_HAND_LEFT = [
    ".o.o.o.o......",
    "oSoSoSoSo.....",
    "oSoSoSoSo.....",
    ".oSsSsSsSo....",
    ".oSSSSSSSoo...",
    ".oSSSSSSSoSo..",
    ".oSSSSSSSSSo..",
    "...oSSSSSSSo..",
    "....oSSSSSo...",
    "....oTTTTTo...",
]
_HAND_RIGHT = [
    ".....o.o.o.o..",
    "....oSoSoSoSo.",
    "....oSoSoSoSo.",
    "...oSsSsSsSo..",
    "...oSSSSSSSoo.",
    "...oSSSSSSSoSo",
    "...oSSSSSSSSSo",
    "...oSSSSSSSo..",
    "....oSSSSSo...",
    "....oTTTTTo...",
]
AVATAR_HANDS = (_HAND_LEFT, _HAND_RIGHT)
AVATAR_HAND_AT = (1, 9)
AVATAR_EYES = [(21, 11), (28, 11)]
AVATAR_COLOURS = {  # sprite char: (CSS class, colour)
    "H": ("hair", "#2e1d15"), "h": ("hairlit", "#543a2e"),
    "S": ("skin", "#d6a086"), "s": ("skindim", "#b07864"),
    "B": ("beard", "#3a2720"), "b": ("stubble", "#7a5446"), "x": ("jaw", "#281a16"),
    "G": ("specs", "#181212"), "E": ("specs", "#181212"),
    "M": ("lips", "#7a342e"), "W": ("teeth", "#ffffff"),
    "N": ("navy", "#1e2746"), "n": ("lapel", "#344470"), "T": ("shirt", "#b6ceec"),
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
