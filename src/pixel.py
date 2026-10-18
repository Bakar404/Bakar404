"""A tiny pixel-art toolkit: a 5x7 bitmap font, sprites, and SVG assembly.

Everything is emitted as merged <path> runs, so the SVGs stay razor sharp at any
zoom and need no web fonts (GitHub serves README images without external assets).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

# Each glyph is 7 rows; "#" is ink. Widths vary so punctuation sits tight.
_GLYPHS = {
    "A": ".###./#...#/#...#/#####/#...#/#...#/#...#",
    "B": "####./#...#/#...#/####./#...#/#...#/####.",
    "C": ".###./#...#/#..../#..../#..../#...#/.###.",
    "D": "####./#...#/#...#/#...#/#...#/#...#/####.",
    "E": "#####/#..../#..../####./#..../#..../#####",
    "F": "#####/#..../#..../####./#..../#..../#....",
    "G": ".###./#...#/#..../#.###/#...#/#...#/.###.",
    "H": "#...#/#...#/#...#/#####/#...#/#...#/#...#",
    "I": "###/.#./.#./.#./.#./.#./###",
    "J": "..###/...#./...#./...#./...#./#..#./.##..",
    "K": "#...#/#..#./#.#../##.../#.#../#..#./#...#",
    "L": "#..../#..../#..../#..../#..../#..../#####",
    "M": "#...#/##.##/#.#.#/#.#.#/#...#/#...#/#...#",
    "N": "#...#/##..#/##..#/#.#.#/#..##/#..##/#...#",
    "O": ".###./#...#/#...#/#...#/#...#/#...#/.###.",
    "P": "####./#...#/#...#/####./#..../#..../#....",
    "Q": ".###./#...#/#...#/#...#/#.#.#/#..#./.##.#",
    "R": "####./#...#/#...#/####./#.#../#..#./#...#",
    "S": ".###./#...#/#..../.###./....#/#...#/.###.",
    "T": "#####/..#../..#../..#../..#../..#../..#..",
    "U": "#...#/#...#/#...#/#...#/#...#/#...#/.###.",
    "V": "#...#/#...#/#...#/#...#/.#.#./.#.#./..#..",
    "W": "#...#/#...#/#...#/#.#.#/#.#.#/##.##/#...#",
    "X": "#...#/#...#/.#.#./..#../.#.#./#...#/#...#",
    "Y": "#...#/#...#/.#.#./..#../..#../..#../..#..",
    "Z": "#####/....#/...#./..#../.#.../#..../#####",
    "0": ".###./#...#/#..##/#.#.#/##..#/#...#/.###.",
    "1": ".#./##./.#./.#./.#./.#./###",
    "2": ".###./#...#/....#/...#./..#../.#.../#####",
    "3": "####./....#/....#/.###./....#/....#/####.",
    "4": "...#./..##./.#.#./#..#./#####/...#./...#.",
    "5": "#####/#..../####./....#/....#/#...#/.###.",
    "6": ".###./#..../#..../####./#...#/#...#/.###.",
    "7": "#####/....#/...#./..#../.#.../.#.../.#...",
    "8": ".###./#...#/#...#/.###./#...#/#...#/.###.",
    "9": ".###./#...#/#...#/.####/....#/....#/.###.",
    ".": "././././././#",
    # The comma and semicolon hang one row below the baseline so "3,3" can't read as "3.3".
    ",": "../../../../../.#/.#/#.",
    ":": "./#/./././#/.",  # centred on the cap height, for scores
    ";": "../../.#/../../.#/.#/#.",
    "!": "#/#/#/#/#/./#",
    "?": ".###./#...#/....#/...#./..#../...../..#..",
    "'": "#/#/././././.",
    '"': "#.#/#.#/.../.../.../.../...",
    "-": "..../..../..../####/..../..../....",
    "+": "...../..#../..#../#####/..#../..#../.....",
    "/": "....#/...#./...#./..#../.#.../.#.../#....",
    "\\": "#..../.#.../.#.../..#../...#./...#./....#",
    "(": "..#/.#./#../#../#../.#./..#",
    ")": "#../.#./..#/..#/..#/.#./#..",
    "[": "###/#../#../#../#../#../###",
    "]": "###/..#/..#/..#/..#/..#/###",
    "<": "...#/..#./.#../#.../.#../..#./...#",
    ">": "#.../.#../..#./...#/..#./.#../#...",
    "=": "...../...../#####/...../#####/...../.....",
    "_": "...../...../...../...../...../...../#####",
    "#": ".#.#./.#.#./#####/.#.#./#####/.#.#./.#.#.",
    "@": ".###./#...#/#.###/#.#.#/#.###/#..../.####",
    "&": ".##../#..#./#.#../.#.../#.#.#/#..#./.##.#",
    "%": "##..#/##..#/...#./..#../.#.../#..##/#..##",
    "*": "...../#.#.#/.###./#####/.###./#.#.#/.....",
    "\u2192": "...../..#../...#./#####/...#./..#../.....",  # right arrow
    "\u2190": "...../..#../.#.../#####/.#.../..#../.....",  # left arrow
    "\u2193": "..#../..#../..#../#.#.#/.###./..#../.....",  # down arrow
    "\u2197": "...../.####/...##/..#.#/.#..#/#..../.....",  # north-east arrow (external link)
    "\u00b7": "./././#/././.",  # middle dot
    "\u25a0": "...../#####/#####/#####/#####/#####/.....",  # solid square (cooperate)
    "\u25a1": "...../#####/#...#/#...#/#...#/#####/.....",  # hollow square (defect)
}
# Faux-bold (below) fills any one-pixel gap, which turns M, W and N into blobs and V into U.
# These glyphs get hand-drawn bold cuts with two-pixel stems instead.
_BOLD = {
    "G": ".####./##..##/##..../##.###/##..##/##..##/.####.",
    "M": "##...##/###.###/#######/##.#.##/##...##/##...##/##...##",
    "N": "##...##/###..##/####.##/##.####/##..###/##...##/##...##",
    "Q": ".####./##..##/##..##/##..##/##.###/##.##./.##.##",
    "R": "#####./##..##/##..##/#####./##.##./##..##/##..##",
    "V": "##...##/##...##/##...##/.##.##./.##.##./..###../...#...",
    "W": "##...##/##...##/##...##/##.#.##/#######/###.###/##...##",
    "0": ".####./##..##/##..##/##..##/##..##/##..##/.####.",
    "4": "##..##/##..##/##..##/######/....##/....##/....##",
    # Faux bold would only widen these to flat dashes.
    ".": "../../../../../##/##",
    ":": "../##/##/../##/##/..",
    "\u00b7": "../../##/##/../../..",
}
FONT = {ch: src.split("/") for ch, src in _GLYPHS.items()}
BOLD_FONT = {ch: src.split("/") for ch, src in _BOLD.items()}
SPACE_WIDTH = 3
GLYPH_HEIGHT = 7


def _glyph(ch: str, bold: bool) -> list[str]:
    rows = FONT.get(ch) or FONT["?"]
    if not bold:
        return rows
    if ch in BOLD_FONT:
        return BOLD_FONT[ch]
    # Faux-bold the classic way: OR every row with itself shifted one pixel right.
    out = []
    for row in rows:
        widened = row + "."
        out.append("".join(
            "#" if widened[i] == "#" or (i > 0 and widened[i - 1] == "#") else "."
            for i in range(len(widened))
        ))
    return out


def text_pixels(text: str, bold: bool = False, tracking: int = 1) -> tuple[set[tuple[int, int]], int]:
    """Lay out text on the font grid. Returns (pixel cells, width in cells)."""
    cells: set[tuple[int, int]] = set()
    x = 0
    for ch in text.upper():
        if ch == " ":
            x += SPACE_WIDTH + tracking
            continue
        rows = _glyph(ch, bold)
        for y, row in enumerate(rows):
            for gx, bit in enumerate(row):
                if bit == "#":
                    cells.add((x + gx, y))
        x += len(rows[0]) + tracking
    return cells, max(0, x - tracking)


def text_width(text: str, u: int, bold: bool = False, tracking: int = 1) -> int:
    return text_pixels(text, bold, tracking)[1] * u


def cells_to_path(cells: Iterable[tuple[int, int]], x0: float, y0: float, u: float) -> str:
    """Merge horizontal runs of cells into compact rectangle subpaths."""
    rows: dict[int, list[int]] = {}
    for cx, cy in cells:
        rows.setdefault(cy, []).append(cx)
    parts = []
    for cy in sorted(rows):
        xs = sorted(rows[cy])
        start = prev = xs[0]
        for cx in xs[1:] + [None]:
            if cx is not None and cx == prev + 1:
                prev = cx
                continue
            w = (prev - start + 1) * u
            parts.append(f"M{_n(x0 + start * u)} {_n(y0 + cy * u)}h{_n(w)}v{_n(u)}h-{_n(w)}z")
            if cx is not None:
                start = prev = cx
    return "".join(parts)


def _n(v: float) -> str:
    return str(int(v)) if float(v).is_integer() else f"{v:.2f}".rstrip("0").rstrip(".")


@dataclass
class Svg:
    """Minimal SVG document builder with a shared, theme-driven stylesheet."""

    width: int
    height: int
    title: str
    theme: dict
    # Set for art that must pick its own colours (a <source> without a colour-scheme query).
    # It also gets an opaque page-colour canvas, so a theme mismatch still stays legible.
    dark: dict | None = None
    css: list[str] = field(default_factory=list)
    defs: list[str] = field(default_factory=list)
    body: list[str] = field(default_factory=list)

    def add(self, element: str) -> None:
        self.body.append(element)

    def path(self, d: str, cls: str, extra: str = "") -> None:
        if d:
            self.add(f'<path class="{cls}" d="{d}"{extra}/>')

    def text(self, s: str, x: float, y: float, u: int, cls: str = "i", *, bold: bool = False,
             tracking: int = 1, anchor: str = "start", extra: str = "") -> int:
        cells, w = text_pixels(s, bold, tracking)
        width = w * u
        if anchor == "middle":
            x -= width / 2
        elif anchor == "end":
            x -= width
        self.path(cells_to_path(cells, x, y, u), cls, extra)
        return width

    def rect(self, x: float, y: float, w: float, h: float, cls: str, extra: str = "") -> None:
        self.add(f'<rect class="{cls}" x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}"{extra}/>')

    def sprite(self, rows: list[str], x: float, y: float, u: int, palette: dict[str, str],
               extra: str = "") -> None:
        layers: dict[str, set[tuple[int, int]]] = {}
        for cy, row in enumerate(rows):
            for cx, ch in enumerate(row):
                if ch in palette:
                    layers.setdefault(palette[ch], set()).add((cx, cy))
        group = [f'<path class="{cls}" d="{cells_to_path(cells, x, y, u)}"/>' for cls, cells in layers.items()]
        self.add(f"<g{extra}>{''.join(group)}</g>")

    def render(self) -> str:
        style = _palette(self.theme)
        if self.dark:
            style += f"@media (prefers-color-scheme:dark){{{_palette(self.dark)}}}"
        style += "".join(dict.fromkeys(self.css)) + "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
        dither = (
            '<pattern id="dither" width="4" height="4" patternUnits="userSpaceOnUse">'
            '<rect class="s" width="2" height="2"/><rect class="s" x="2" y="2" width="2" height="2"/>'
            "</pattern>"
        )
        canvas = '<rect class="c" width="100%" height="100%"/>' if self.dark else ""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}" shape-rendering="crispEdges" role="img" '
            f'aria-labelledby="t"><title id="t">{_escape(self.title)}</title>'
            f"<style>{style}</style><defs>{dither}{''.join(self.defs)}</defs>"
            f"{canvas}{''.join(self.body)}</svg>\n"
        )


def _palette(t: dict) -> str:
    return (
        f".i{{fill:{t['ink']}}}.m{{fill:{t['muted']}}}.a{{fill:{t['accent']}}}"
        f".k{{fill:{t['accent_ink']}}}.p{{fill:{t['panel']}}}.g{{fill:{t['grid']}}}"
        f".s{{fill:{t['shade']}}}.c{{fill:{t['canvas']}}}.d{{fill:url(#dither)}}"
        f".o{{fill:{t['accent_side']}}}.e{{fill:{t['panel_side']}}}"
        f".h{{fill:{t['hot']}}}.n{{fill:{t['hot_ink']}}}"
    )


def _escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


THEMES = {
    # Light is 1-bit: ink on white paper. Dark is its inverse, except the key sides, which turn
    # ochre instead of glaring white.
    "light": {
        "ink": "#1f2328", "muted": "#59636e", "accent": "#ffc72c", "accent_ink": "#1f2328",
        "panel": "#ffffff", "grid": "#d1d9e0", "shade": "#818b98", "canvas": "#ffffff",
        "accent_side": "#1f2328", "panel_side": "#1f2328", "hot": "#1f2328", "hot_ink": "#ffffff",
    },
    "dark": {
        "ink": "#e6edf3", "muted": "#9198a1", "accent": "#ffc72c", "accent_ink": "#0d1117",
        "panel": "#161b22", "grid": "#30363d", "shade": "#545d68", "canvas": "#0d1117",
        "accent_side": "#8a6a00", "panel_side": "#3d444d", "hot": "#e6edf3", "hot_ink": "#0d1117",
    },
}
