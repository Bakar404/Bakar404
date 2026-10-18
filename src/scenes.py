"""Compose every README scene as an SVG string.

Desktop scenes are W px wide, the width of a profile README on desktop GitHub, so they render
1:1 there. The README sizes every image in percent, so on narrower screens they scale as one.

Phones get their own layouts, M = W / 2 wide, so they come out at twice the desktop scale.
Phone art is served from a <source> without a colour-scheme query, so it is drawn with
theme="auto": it carries both palettes and picks one itself.
"""
from __future__ import annotations

from itertools import combinations

import pd
import sprites
from pixel import SPACE_WIDTH, THEMES, Svg, cells_to_path, text_pixels, text_width

W = 846
M = W // 2
PAD = 32
MPAD = 20
SUMMARY_W = 760  # wider than its text so the phone version can use larger type
PAL = sprites.PALETTE
PAST = {"C": "COOPERATED", "D": "DEFECTED"}

# Copy is stored in normal case for alt text; the pixel font renders it in capitals.
NAME = "Ahmed Abdelsalam"
TAGLINE = "Cooperate or defect? The bot remembers."
SUMMARY = "How does the bot decide?"
INTERESTS = [  # caption lines, icon, its selected frame
    (("Being", "creative"), sprites.PEN_NIB, sprites.PEN_NIB_ON),
    (("Building", "with AI"), sprites.CHIP, sprites.CHIP_ON),
    (("Building cool", "products"), sprites.TOGGLES, sprites.TOGGLES_ON),
    (("Game", "theory"), sprites.MATRIX, sprites.MATRIX_ON),
]
TOOLS = [
    ("Languages", ["Python", "TypeScript", "JavaScript", "Swift", "SQL", "C++", "DAX", "HTML/CSS"]),
    ("Build", ["React", "Node.js", "FastAPI", "SwiftUI", "CoreAudio", "Tailwind", "Supabase",
               "Firebase", "GitHub Actions"]),
    ("Data + AI", ["MCP", "LLM agents", "Azure", "Fabric", "Power BI", "Data Factory", "Synapse",
                   "Databricks", "pandas", "NumPy", "SciPy"]),
]
ANYTHING = "+ Anything that gets the job done"

BLINK = "@keyframes blink{50%{opacity:0}}"
TYPE = "@keyframes type{from{opacity:0}to{opacity:1}}"
BOB = "@keyframes bob{50%{transform:translateY(-4px)}}"
BLINKING = ' style="animation:blink 1.06s step-end infinite"'
BOBBING = [BOB, ".bob{animation:bob 1.2s step-end infinite}",
           ".bob2{animation:bob 1.2s step-end .6s infinite}"]


def canvas(w: int, h: int, title: str, theme: str) -> Svg:
    """theme is "light", "dark", or "auto" for art that has to pick its own colours."""
    if theme == "auto":
        return Svg(w, h, title, THEMES["light"], dark=THEMES["dark"])
    return Svg(w, h, title, THEMES[theme])


def notched(x: float, y: float, w: float, h: float, n: float) -> str:
    """Rectangle with two-step pixel corners."""
    return (
        f"M{x + 2 * n} {y}h{w - 4 * n}v{n}h{n}v{n}h{n}v{h - 4 * n}h-{n}v{n}h-{n}v{n}"
        f"h-{w - 4 * n}v-{n}h-{n}v-{n}h-{n}v-{h - 4 * n}h{n}v-{n}h{n}z"
    )


def section_label(s: Svg, text: str, y: float) -> None:
    s.text(text, 0, y, 2, "m", bold=True)


def staircase(x: float, y: float, w: float, h: float, u: int) -> str:
    """A pixel diagonal from the top-left to the bottom-right corner of a box."""
    nx, ny = int(w // u), int(h // u)
    return cells_to_path({(i, round(i * (ny - 1) / (nx - 1))) for i in range(nx)}, x, y, u)


def runs(s: Svg, parts: list[tuple[str, str, bool]], x: float, y: float, u: int,
         anchor: str = "start") -> None:
    """One line of text made of differently styled runs: (text, class, bold)."""
    widths = [text_pixels(t, b)[1] * u for t, _, b in parts]
    total = sum(widths) + u * (len(parts) - 1)
    x -= total / 2 if anchor == "middle" else total if anchor == "end" else 0
    for (text, cls, bold), w in zip(parts, widths):
        s.text(text, x, y, u, cls, bold=bold)
        x += w + u


def typed(s: Svg, text: str, x: float, y: float, u: int, *, cls: str = "i", cursor: str = "i",
          delay: float = 0.4, per: float = 0.055, caret: bool = True) -> float:
    """Text that types itself out, followed by a blinking block cursor.

    Returns when the last character appears, so a following line can start there.
    With reduced motion everything simply renders in its final state.
    """
    stops, cx = [], x
    for i, ch in enumerate(text.upper()):
        cells, w = text_pixels(ch)
        if ch == " ":
            w = SPACE_WIDTH
        at = delay + (i + 1) * per
        if cells:
            # Hidden for the whole duration, then flips on and stays. Short animations with a
            # delay get dropped by Chrome inside <img> SVGs, so avoid delays entirely.
            s.path(cells_to_path(cells, cx, y, u), cls,
                   f' style="animation:type {at:.3f}s step-end both"')
        cx += (w + 1) * u
        stops.append(cx)
    end = cx + u
    n = len(stops)
    frames = [f"0%{{transform:translateX({x - end + u}px)}}"]
    frames += [
        f"{100 * (i + 1) / (n + 1):.3f}%{{transform:translateX({stop - end + u}px)}}"
        for i, stop in enumerate(stops)
    ]
    frames.append("100%{transform:translateX(0)}")
    total = (n + 1) * per
    s.css.extend([TYPE, BLINK])
    if caret:
        name = f"caret{len(s.css)}"
        s.css.append(f"@keyframes {name}{{" + "".join(frames) + "}")
        # hidden until its line starts, then it walks along and blinks
        s.rect(end, y, 4 * u, 7 * u, cursor,
               f' style="animation:type {delay:.3f}s step-end both,'
               f' {name} {total:.3f}s step-end {delay:.3f}s both,'
               f' blink 1.06s step-end {delay + total:.3f}s infinite"')
    return delay + n * per


# ----------------------------------------------------------------------------- header

def name(theme: str) -> str:
    u = 9  # 92 cells
    s = canvas(W, 7 * u + 24, NAME, theme)
    display(s, NAME, 0, 0, u)
    return s.render()


def name_mobile() -> str:
    """Stacked, so a phone can show it larger than one line would allow."""
    u = 7  # ABDELSALAM is 59 cells
    first, last = NAME.split()
    s = canvas(M, 17 * u + 16, NAME, "auto")
    display(s, first, 0, 0, u)
    display(s, last, 0, 10 * u, u)
    return s.render()


def display(s: Svg, text: str, x: float, y: float, u: int) -> None:
    cells, _ = text_pixels(text)
    s.path(cells_to_path(cells, x, y, u), "i")


def tagline(theme: str) -> str:
    s = canvas(W, 24, TAGLINE, theme)
    typed(s, TAGLINE, 0, 0, 3)
    return s.render()


def tagline_mobile() -> str:
    """Two lines, the second typing on where the first stops."""
    first, second = TAGLINE.split("? ")
    s = canvas(M, 24 + 31, TAGLINE, "auto")
    done = typed(s, f"{first}?", 0, 0, 3, caret=False)
    typed(s, second, 0, 31, 3, delay=done)
    return s.render()


# ------------------------------------------------------------------------------ board

def matrix(s: Svg, last: dict | None, mx: float, ay: float, cw: int, ch: int, gap: int,
           left: float | None = None) -> float:
    """Payoff matrix in Schelling's notation, your payoff bottom-left and the bot's top-right,
    with its labels. The last round's outcome is highlighted. Returns the bottom edge.

    Labels hug the matrix unless `left` is given, which lines them up on that edge instead.
    """
    g = 4
    my = ay + 14 + gap
    lx, anchor = (mx - gap, "end") if left is None else (left, "start")
    s.text("YOU \\ BOT", lx, ay, 2, "m", anchor=anchor)
    for c, word in enumerate(("COOPERATE", "DEFECT")):
        s.text(word, mx + g + c * (cw + g) + cw // 2, ay, 2, bold=True, anchor="middle")
    for r, word in enumerate(("COOPERATE", "DEFECT")):
        s.text(word, lx, my + g + r * (ch + g) + (ch - 14) // 2, 2, bold=True, anchor=anchor)
    s.rect(mx, my, 2 * cw + 3 * g, 2 * ch + 3 * g, "i")
    for r, you in enumerate("CD"):
        for c, bot in enumerate("CD"):
            x, y = mx + g + c * (cw + g), my + g + r * (ch + g)
            hot = last is not None and (last["human"], last["bot"]) == (you, bot)
            s.rect(x, y, cw, ch, "h" if hot else "p")
            s.path(staircase(x, y, cw, ch, 4), "m" if hot else "g")
            mine, theirs = pd.PAYOFFS[(you, bot)]
            s.text(str(mine), x + 12, y + ch - 12 - 28, 4, "n" if hot else "i", bold=True)
            s.text(str(theirs), x + cw - 12, y + 12, 3, "n" if hot else "m", bold=True,
                   anchor="end")
    return my + 2 * ch + 3 * g


def tile(s: Svg, x: float, y: float, move: str) -> None:
    """A move in the history: solid if it cooperated, hollow if it defected."""
    if move == "C":
        s.rect(x, y, 16, 16, "i")
    else:
        s.path(f"M{x} {y}h16v16h-16zM{x + 4} {y + 4}v8h8v-8z", "i", ' fill-rule="evenodd"')


def your_move(s: Svg, x: float, y: float, extra: str = BLINKING) -> None:
    s.add(f"<g{extra}>")
    s.rect(x, y, 16, 16, "i")
    s.rect(x + 2, y + 2, 12, 12, "a")
    s.add("</g>")


def history(s: Svg, state: dict, x0: float, x1: float, y: float) -> None:
    """The most recent moves that fit between the edges, oldest first, then the round being
    played right now."""
    sx = x0 + text_width("HUMANS", 2, bold=True) + 16
    slots = int(x1 - sx + 4) // 20
    recent = state["history"][-(slots - 1):] if slots > 1 else []
    for row, (key, label) in enumerate((("human", "HUMANS"), ("bot", "BOT"))):
        ty = y + row * 24
        s.text(label, x0, ty + 1, 2, "m", bold=True)
        for i, move in enumerate(recent):
            tile(s, sx + i * 20, ty, move[key])
    nx = sx + len(recent) * 20
    your_move(s, nx, y)
    s.text("?", nx + 3, y + 25, 2, extra=BLINKING)


def legend_tiles(s: Svg, x: float, y: float) -> None:
    for move in "CD":
        tile(s, x, y, move)
        x += 24 + s.text(PAST[move], x + 24, y + 1, 2, "m") + 24


def legend_turn(s: Svg, x: float, y: float, anchor: str = "start") -> None:
    if anchor == "end":
        x -= 24 + text_width("YOUR MOVE", 2) + 24 + 24 + text_width("BOT HAS CHOSEN", 2)
    your_move(s, x, y, extra="")
    x += 24 + s.text("YOUR MOVE", x + 24, y + 1, 2) + 24
    s.text("?", x + 3, y + 1, 2)
    s.text("BOT HAS CHOSEN", x + 24, y + 1, 2, "m")


def card(s: Svg, top: float) -> None:
    """Frame everything drawn so far in a notched card from `top` to the bottom edge."""
    s.body[:0] = [f'<path class="i" d="{notched(0, top, s.width, s.height - top, 4)}"/>',
                  f'<path class="p" d="{notched(4, top + 4, s.width - 8, s.height - top - 8, 4)}"/>']


def score(s: Svg, state: dict, mid: float, y: float, room: float, sizes: tuple[int, ...]) -> None:
    """67:62, the colon on `mid`, as large as `room` allows, vertically centred on a 64px row."""
    humans, bot = (str(state["totals"][k]) for k in ("humans", "bot"))
    longest = max(humans, bot, key=len)
    u = next((u for u in sizes if 2 * (text_width(longest, u, bold=True) + 3 * u) <= room),
             sizes[-1])
    sy = y + (64 - 7 * u) // 2
    s.text(":", mid, sy, u, bold=True, anchor="middle")
    s.text(humans, mid - 3 * u, sy, u, bold=True, anchor="end")
    s.text(bot, mid + 3 * u, sy, u, bold=True)


def board(state: dict, theme: str) -> str:
    top = 48  # breathing room under the tagline
    s = canvas(W, 0, board_alt(state), theme)
    s.css.extend([BLINK, *BOBBING])
    last = state["history"][-1] if state["history"] else None
    mood = pd.bot_mood(state)
    x0, x1 = PAD, W - PAD

    y = top + 32
    s.text("PRISONER'S DILEMMA", x0, y, 3, bold=True)
    s.text(facts(state), x0, y + 33, 2, "m")
    y += 47 + 28
    s.rect(x0, y, x1 - x0, 4, "g")

    # face-off: the humans, the score, the bot
    y += 4 + 32
    s.sprite(sprites.HUMAN, x0, y, 4, PAL, ' class="bob"')
    s.sprite(bot_sprite(mood), x1 - 64, y, 4, PAL, ' class="bob2"')
    s.text("HUMANS", x0 + 80, y + 10, 3, bold=True)
    s.text("UNDECIDED", x0 + 80, y + 39, 2, "m")
    s.text("BOT", x1 - 80, y + 10, 3, bold=True, anchor="end")
    s.text(mood.upper(), x1 - 80, y + 39, 2, "m", anchor="end")
    side = 80 + max(text_width("HUMANS", 3, bold=True), text_width("UNDECIDED", 2)) + 32
    score(s, state, W // 2, y, x1 - x0 - 2 * side, (6, 5, 4))
    y += 64 + 40

    # the matrix, centred with its row labels
    cw, ch, gap = 144, 88, 16
    lw = text_width("COOPERATE", 2, bold=True)
    gx = (W - (lw + gap + 2 * cw + 12)) // 2
    bottom = matrix(s, last, gx + lw + gap, y, cw, ch, gap)

    y = bottom + 24
    if last:
        runs(s, [("LAST ROUND", "m", False),
                 (f" @{last['player'][:20]} {PAST[last['human']]}, BOT {PAST[last['bot']]}",
                  "i", False)], W // 2, y, 2, "middle")
    else:
        s.text("NO MOVES YET. BE THE FIRST TO PLAY", W // 2, y, 2, anchor="middle")
    y += 14 + 24
    s.rect(x0, y, x1 - x0, 4, "g")

    y += 4 + 28
    history(s, state, x0, x1, y)
    y += 40 + 20
    legend_tiles(s, x0, y)
    legend_turn(s, x1, y, anchor="end")
    s.height = y + 16 + 28
    card(s, top)
    return s.render()


def board_mobile(state: dict) -> str:
    """The same board for phones: title, then a face-off with the score, then the matrix."""
    top = 32
    s = canvas(M, 0, board_alt(state), "auto")
    s.css.extend([BLINK, *BOBBING])
    last = state["history"][-1] if state["history"] else None
    mood = pd.bot_mood(state)
    x0, x1 = MPAD, M - MPAD
    mid = M // 2

    y = top + 20
    s.text("PRISONER'S DILEMMA", x0, y, 3, bold=True)
    y += 21 + 10
    s.text(facts(state), x0, y, 2, "m")
    y += 14 + 18
    s.rect(x0, y, x1 - x0, 4, "g")

    # face-off: the humans, the score, the bot
    y += 4 + 20
    s.sprite(sprites.HUMAN, x0 - 4, y, 4, PAL, ' class="bob"')
    s.sprite(bot_sprite(mood), x1 - 60, y, 4, PAL, ' class="bob2"')
    score(s, state, mid, y, x1 - x0 - 152, (5, 4, 3))
    s.text("HUMANS", x0, y + 76, 2, bold=True)
    s.text("BOT", x1, y + 76, 2, bold=True, anchor="end")
    s.text("UNDECIDED", x0, y + 98, 2, "m")
    s.text(mood.upper(), x1, y + 98, 2, "m", anchor="end")

    cw, ch = 116, 72
    lw = text_width("COOPERATE", 2, bold=True)
    gx = (M - (lw + 12 + 2 * cw + 12)) // 2
    y = matrix(s, last, gx + lw + 12, y + 112 + 24, cw, ch, 12, left=gx) + 20
    if last:
        last_round_tiles(s, last, mid, y, x1 - x0)
    else:
        s.text("NO MOVES YET. BE THE FIRST", mid, y, 2, anchor="middle")
    y += 14 + 20
    s.rect(x0, y, x1 - x0, 4, "g")

    y += 4 + 20
    history(s, state, x0, x1, y)
    y += 40 + 16
    legend_tiles(s, x0, y)
    y += 16 + 12
    legend_turn(s, x0, y)
    s.height = y + 16 + 20
    card(s, top)
    return s.render()


def last_round_tiles(s: Svg, last: dict, cx: float, y: float, room: float) -> None:
    """LAST ROUND @player [move] BOT [move] on one centred line, the moves drawn as history
    tiles. The name is shortened if the line would not fit in `room`."""
    player = f"@{last['player']}"
    def width(name: str) -> int:
        return (text_width("LAST ROUND", 2) + 12 + text_width(name, 2) + 8 + 16 + 16
                + text_width("BOT", 2) + 8 + 16)
    while width(player) > room and len(player) > 2:
        player = player[:-1]
    x = cx - width(player) // 2
    x += s.text("LAST ROUND", x, y, 2, "m") + 12
    x += s.text(player, x, y, 2) + 8
    tile(s, x, y - 1, last["human"])
    x += 16 + 16
    x += s.text("BOT", x, y, 2) + 8
    tile(s, x, y - 1, last["bot"])


def facts(state: dict) -> str:
    if not state["round"]:
        return "ROUND 0 \u00b7 NO PLAYERS YET"
    players = len(state["players"])
    return (f"ROUND {state['round']} \u00b7 {players} PLAYER{'' if players == 1 else 'S'}"
            f" \u00b7 {pd.cooperation_rate(state)}% CO-OP")


def bot_sprite(mood: str) -> list[str]:
    return sprites.BOT_SUSPICIOUS if mood == "suspicious" else sprites.BOT


def board_alt(state: dict) -> str:
    if not state["history"]:
        return ("Prisoner's Dilemma against a bot. No moves yet: be the first to play "
                "with the buttons below.")
    last = state["history"][-1]
    return (
        f"Prisoner's Dilemma against a bot, round {state['round']}. Last round: "
        f"@{last['player']} {pd.PAST[last['human']]}, the bot {pd.PAST[last['bot']]}. "
        f"Humans {state['totals']['humans']} points, bot {state['totals']['bot']}. "
        f"{pd.cooperation_rate(state)}% of moves were cooperative. The bot is "
        f"{pd.bot_mood(state)}."
    )


# ---------------------------------------------------------------------------- buttons

def button(move: str, theme: str) -> str:
    """Half of a full-width keypad under the board. Both keys look alike so neither choice
    is nudged; only the tile and the word tell them apart."""
    return key(move, theme, W // 2, top=8, h=56, side=8, u=3)


def button_mobile(move: str) -> str:
    return key(move, "auto", (M + 1) // 2, top=12, h=60, side=8, u=2)


def key(move: str, theme: str, width: int, *, top: int, h: int, side: int, u: int) -> str:
    label = "\u25a0 COOPERATE" if move == "C" else "\u25a1 DEFECT"
    s = canvas(width, top + h, "Cooperate" if move == "C" else "Defect", theme)
    gutter = 8
    x, w = (0, width - gutter // 2) if move == "C" else (gutter // 2, width - gutter // 2)
    fx, fy, fw, fh = x + 4, top + 4, w - 8, h - 8 - side
    s.path(notched(x, top, w, h, 4), "i")
    s.path(notched(fx, fy, fw, h - 8, 3), "o")  # the key's side
    s.path(notched(fx, fy, fw, fh, 3), "a")
    s.text(label, fx + fw / 2, fy + (fh - 7 * u) / 2, u, "k", bold=True, anchor="middle")
    return s.render()


def summary(theme: str) -> str:
    s = canvas(SUMMARY_W, 14, SUMMARY, theme)
    s.text(SUMMARY, 0, 0, 2, bold=True)
    return s.render()


def summary_mobile() -> str:
    s = canvas(SUMMARY_W // 2, 14, SUMMARY, "auto")
    s.text(SUMMARY, 0, 0, 2, bold=True)
    return s.render()


# ------------------------------------------------------------------------- spec sheet

def specs(theme: str) -> str:
    s = canvas(W, 0, specs_alt(), theme)
    y = 32
    section_label(s, "INTERESTS", y)
    y = interests(s, y + 14 + 24, W, cols=2, gap=32) + 64
    section_label(s, "TOOLS", y)
    y += 14 + 24
    col = max(text_width(label, 2, bold=True) for label, _ in TOOLS) + 32
    for label, items in TOOLS:
        s.text(label, 0, y, 2, bold=True)
        for line in flow(items, W - col, 2):
            s.text(line, col, y, 2)
            y += 24
        y += 16
    s.text(ANYTHING, col, y, 2, bold=True)
    s.height = y + 14 + 8
    return s.render()


def specs_mobile() -> str:
    s = canvas(M, 0, specs_alt(), "auto")
    y = 24
    section_label(s, "INTERESTS", y)
    y = interests(s, y + 14 + 24, M, cols=1, gap=24) + 48
    section_label(s, "TOOLS", y)
    y += 14 + 24
    for label, items in TOOLS:
        s.text(label, 0, y, 2, bold=True)
        y += 24
        for line in flow(items, M, 2):
            s.text(line, 0, y, 2)
            y += 24
        y += 16
    first, rest = ANYTHING.rsplit(" the ", 1)
    lines = [ANYTHING] if text_width(ANYTHING, 2, bold=True) <= M else [first, f"the {rest}"]
    for line in lines:
        s.text(line, 0, y, 2, bold=True)
        y += 24
    s.height = y - 10 + 8
    return s.render()


def interests(s: Svg, y: float, width: int, cols: int, gap: int) -> float:
    """A menu of icons with two-line captions, in reading order. Like a game's attract mode,
    each item takes a turn being selected: its icon hops and switches to its selected frame.
    Returns the bottom edge."""
    n, u, box = len(INTERESTS), 4, 64
    period = f"{2 * n}s step-end infinite"
    for i, (lines, icon, selected) in enumerate(INTERESTS):
        r, c = divmod(i, cols)
        x, top = c * (width // cols), y + r * (box + gap)
        on, off = f"{100 * i / n:g}%", f"{100 * (i + 1) / n:g}%"
        for name, rest, picked in (("hop", "transform:none", f"transform:translateY(-{u}px)"),
                                   ("show", "opacity:0", "opacity:1"),
                                   ("hide", "opacity:1", "opacity:0")):
            first = f"0%{{{rest}}}" if i else ""
            s.css.append(f"@keyframes {name}{i}{{{first}{on}{{{picked}}}{off}{{{rest}}}}}")
        ix, iy = x + (box - len(icon[0]) * u) // 2, top + (box - len(icon) * u) // 2
        s.add(f'<g style="animation:hop{i} {period}">')
        s.sprite(icon, ix, iy, u, PAL, f' style="animation:hide{i} {period}"')
        # hidden unless animated, so reduced motion shows the plain icon
        s.sprite(selected, ix, iy, u, PAL, f' style="opacity:0;animation:show{i} {period}"')
        s.add("</g>")
        for j, line in enumerate(lines):
            s.text(line, x + box + 24, top + 14 + j * 22, 2, bold=True)
    return y + (n - 1) // cols * (box + gap) + box


def flow(items: list[str], width: int, u: int, sep: str = " \u00b7 ") -> list[str]:
    """Break items into as few lines as fit `width`, as even as possible so no item is
    stranded on a line of its own. Earlier lines take the extra when there is a tie."""
    def widest(cuts: tuple[int, ...]) -> tuple[int, list[str]]:
        cuts = tuple(sorted(cuts))
        lines = [sep.join(items[a:b]) for a, b in zip((0, *cuts), (*cuts, len(items)))]
        return max(text_width(line, u) for line in lines), lines

    for n in range(len(items)):
        splits = [widest(cuts) for cuts in combinations(range(len(items) - 1, 0, -1), n)]
        fits = [split for split in splits if split[0] <= width]
        if fits:
            return min(fits, key=lambda split: split[0])[1]
    return items


def specs_alt() -> str:
    names = [" ".join(lines) for lines, *_ in INTERESTS]
    names = [n[0].lower() + n[1:] for n in names]
    tools = " ".join(f"{label}: {', '.join(items)}." for label, items in TOOLS)
    return (f"Interests: {', '.join(names[:-1])} and {names[-1]}. Tools. {tools} "
            f"{ANYTHING}.")
