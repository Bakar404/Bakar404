"""Compose every README scene as an SVG string.

Desktop scenes are W px wide, the width of a profile README on desktop GitHub, so they render
1:1 there. The README sizes every image in percent, so on narrower screens they scale as one.

Phones get their own layouts, M = W / 2 wide, so they come out at twice the desktop scale.
Phone art is served from a <source> without a colour-scheme query, so it is drawn with
theme="auto": it carries both palettes and picks one itself.
"""
from __future__ import annotations

from itertools import combinations

import nim
import sprites
from pixel import SPACE_WIDTH, THEMES, Svg, cells_to_path, text_pixels, text_width

W = 846
M = W // 2
PAD = 32
MPAD = 20
SUMMARY_W = 760  # wider than its text so the phone version can use larger type
PAL = sprites.PALETTE
KEY_W = W // 6  # the keypad under the board: a label and up to five keys per row
KEY_M = M // 6

# Copy is stored in normal case for alt text; the pixel font renders it in capitals.
NAME = "Ahmed Abdelsalam"
LINE = "Hi, I'm Ahmed. I turn ideas into products, mostly with AI."
SUMMARY = "How does the bot decide?"
INTERESTS = [  # caption lines, icon, its selected frame
    (("Being", "creative"), sprites.PEN_NIB, sprites.PEN_NIB_ON),
    (("Building", "with AI"), sprites.CHIP, sprites.CHIP_ON),
    (("Building cool", "products"), sprites.TOGGLES, sprites.TOGGLES_ON),
    (("Game", "theory"), sprites.MATRIX, sprites.MATRIX_ON),
]
TOOLS = [
    ("AI + agents", ["MCP", "LLM agents", "Multi-agent orchestration", "Agent evals",
                     "Microsoft Agent Framework", "Anthropic API", "Azure AI"]),
    ("Languages", ["Python", "TypeScript", "JavaScript", "Swift", "SQL", "C++", "R", "DAX",
                   "HTML/CSS"]),
    ("Build", ["React", "Next.js", "Vite", "Tailwind", "Node.js", "FastAPI", "SwiftUI",
               "CoreAudio"]),
    ("Data + cloud", ["Azure", "Microsoft Fabric", "Power BI", "Power Platform", "Data Factory",
                      "Synapse", "Databricks", "pandas", "NumPy", "SciPy"]),
    ("Ship", ["Supabase", "Firebase", "Cloudflare Workers", "GitHub Actions", "Playwright",
              "Git", "Azure DevOps", "Jira"]),
]
ANYTHING = "+ Anything that gets the job done"

BLINK = "@keyframes blink{50%{opacity:0}}"
TYPE = "@keyframes type{from{opacity:0}to{opacity:1}}"
BOB = "@keyframes bob{50%{transform:translateY(-4px)}}"
BLINKING = ' style="animation:blink 1.06s step-end infinite"'
BOBBING = [BOB, ".bob{animation:bob 1.2s step-end infinite}",
           ".bob2{animation:bob 1.2s step-end .6s infinite}"]
# The avatar waves three times, rests, and blinks once in a while. Frame changes every 0.4s.
WAVE = 4.8
WAVING = [
    "@keyframes wave-l{0%{opacity:1}8.333%{opacity:0}16.667%{opacity:1}25%{opacity:0}"
    "33.333%{opacity:1}41.667%{opacity:0}50%{opacity:1}}",
    "@keyframes wave-r{0%{opacity:0}8.333%{opacity:1}16.667%{opacity:0}25%{opacity:1}"
    "33.333%{opacity:0}41.667%{opacity:1}50%{opacity:0}}",
    "@keyframes lids{0%{opacity:1}72%{opacity:0}75%{opacity:1}}",
]
TAIL = [  # the speech box's tail, pointing at the speaker; column 5 is the box's left edge
    ".....#",
    "....#p",
    "...#pp",
    "..#ppp",
    ".#pppp",
    "######",
]
NEXT = {(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (1, 1), (2, 1), (3, 1), (2, 2)}  # the RPG ▼


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


def runs_width(parts: list[tuple[str, str, bool]], u: int) -> int:
    return (sum(text_width(t, u, b) for t, _, b in parts)
            + (SPACE_WIDTH + 2) * u * (len(parts) - 1))


def runs(s: Svg, parts: list[tuple[str, str, bool]], x: float, y: float, u: int,
         anchor: str = "start") -> None:
    """One line of text made of differently styled runs, (text, class, bold), a space apart."""
    total = runs_width(parts, u)
    x -= total / 2 if anchor == "middle" else total if anchor == "end" else 0
    for text, cls, bold in parts:
        s.text(text, x, y, u, cls, bold=bold)
        x += text_width(text, u, bold) + (SPACE_WIDTH + 2) * u


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


# ------------------------------------------------------------------------------- hero

def hero_alt() -> str:
    return f'{NAME}, drawn in pixels, waving: "{LINE}"'


def avatar(s: Svg, x: float, y: float, u: int) -> None:
    """The portrait: waving, and blinking now and then. Reduced motion keeps the first frame."""
    s.css.extend([sprites.AVATAR_CSS, *WAVING])
    pal = sprites.AVATAR_PALETTE
    s.sprite(sprites.AVATAR, x, y, u, pal)
    hx, hy = x + sprites.AVATAR_HAND_AT[0] * u, y + sprites.AVATAR_HAND_AT[1] * u
    left, right = sprites.AVATAR_HANDS
    s.sprite(left, hx, hy, u, pal, f' style="animation:wave-l {WAVE}s step-end infinite"')
    s.sprite(right, hx, hy, u, pal, f' style="opacity:0;animation:wave-r {WAVE}s step-end infinite"')
    s.path(cells_to_path(sprites.AVATAR_EYES, x, y, u), "specs",
           f' style="animation:lids {WAVE}s step-end infinite"')


def speech(s: Svg, lines: list[str], x: float, y: float, w: float, u: int, pad: int,
           tail_y: float) -> float:
    """An RPG dialog box that types `lines` out, then blinks its ▼. Returns its bottom edge."""
    lh = 7 * u + 4 * u
    h = 8 + 2 * pad + len(lines) * lh - 4 * u
    s.path(notched(x, y, w, h, 4), "i")
    s.path(notched(x + 4, y + 4, w - 8, h - 8, 4), "p")
    s.sprite(TAIL, x - 20, tail_y, 4, {"#": "i", "p": "p"})
    at = 0.6
    for i, line in enumerate(lines):
        at = typed(s, line, x + 4 + pad, y + 4 + pad + i * lh, u, caret=False, delay=at)
    s.css.extend([TYPE, BLINK])
    s.path(cells_to_path(NEXT, x + w - 4 - pad + u - 5 * u, y + h - 4 - pad + 4 * u - 3 * u, u), "i",
           f' style="animation:type {at:.3f}s step-end both,blink 1.06s step-end {at:.3f}s infinite"')
    return y + h


def wrap(text: str, width: float, u: int) -> list[str]:
    return flow(text.split(), width, u, sep=" ")


def hero(theme: str) -> str:
    u = 5
    aw, ah = len(sprites.AVATAR[0]) * u, len(sprites.AVATAR) * u
    s = canvas(W, 0, hero_alt(), theme)
    x = aw + 32
    display(s, NAME, x, u + 8, 6)
    pad = 20
    lines = wrap(LINE, W - x - 8 - 2 * pad, 3)
    top = u + 8 + 42 + 24
    bottom = speech(s, lines, x, top, W - x, 3, pad, tail_y=top + 12)
    ay = max(0, bottom - ah)  # the portrait stands on the box's baseline
    avatar(s, 0, ay, u)
    s.height = int(max(bottom, ay + ah)) + 8
    return s.render()


def hero_mobile() -> str:
    """Name stacked on top, so it can be large; the portrait and its speech box below."""
    nu, u = 7, 3
    first, last = NAME.split()
    aw, ah = len(sprites.AVATAR[0]) * u, len(sprites.AVATAR) * u
    s = canvas(M, 0, hero_alt(), "auto")
    display(s, first, 0, 0, nu)
    display(s, last, 0, 10 * nu, nu)
    y = 17 * nu + 16
    avatar(s, 0, y, u)
    x, pad = aw + 20, 14
    lines = wrap(LINE, M - x - 8 - 2 * pad, 2)
    bottom = speech(s, lines, x, y + u, M - x, 2, pad, tail_y=y + 12 * u)
    s.height = int(max(bottom, y + ah)) + 8
    return s.render()


def display(s: Svg, text: str, x: float, y: float, u: int) -> None:
    cells, _ = text_pixels(text)
    s.path(cells_to_path(cells, x, y, u), "i")


# ------------------------------------------------------------------------------ board

def card(s: Svg, top: float) -> None:
    """Frame everything drawn so far in a notched card from `top` to the bottom edge."""
    s.body[:0] = [f'<path class="i" d="{notched(0, top, s.width, s.height - top, 4)}"/>',
                  f'<path class="p" d="{notched(4, top + 4, s.width - 8, s.height - top - 8, 4)}"/>']


def score(s: Svg, state: dict, mid: float, y: float, room: float, sizes: tuple[int, ...]) -> None:
    """3:5, the colon on `mid`, as large as `room` allows, vertically centred on a 64px row."""
    humans, bot = (str(state["wins"][k]) for k in ("humans", "bot"))
    longest = max(humans, bot, key=len)
    u = next((u for u in sizes if 2 * (text_width(longest, u, bold=True) + 3 * u) <= room),
             sizes[-1])
    sy = y + (64 - 7 * u) // 2
    s.text(":", mid, sy, u, bold=True, anchor="middle")
    s.text(humans, mid - 3 * u, sy, u, bold=True, anchor="end")
    s.text(bot, mid + 3 * u, sy, u, bold=True)


def your_move(s: Svg, x: float, y: float) -> None:
    s.add(f"<g{BLINKING}>")
    s.rect(x, y, 16, 16, "i")
    s.rect(x + 2, y + 2, 12, 12, "a")
    s.add("</g>")


def bits_width(u: int, pitch: int) -> int:
    """The nim-sum table's width: a column per bit of the largest heap."""
    return (len(bin(nim.MAX_HEAP)) - 3) * pitch + 7 * u


def heaps(s: Svg, state: dict, x: float, y: float, u: int, pitch: int, row_gap: int,
          bits_x: float, bit_u: int, bit_pitch: int) -> float:
    """Each heap as a row of matches, the ones already taken as ghosts, with its size in binary
    on the right; then the nim-sum. Returns the bottom edge."""
    mw, mh = len(sprites.MATCH[0]) * u, len(sprites.MATCH) * u
    start = nim.STARTS[(state["game"] - 1) % len(nim.STARTS)]
    width = len(bin(nim.MAX_HEAP)) - 2
    for i, place in enumerate(2 ** b for b in reversed(range(width))):
        s.text(str(place), bits_x + i * bit_pitch + 7 * bit_u // 2, y, 2, "m", anchor="middle")
    y += 14 + 16
    for row, (size, full) in enumerate(zip(state["heaps"], start)):
        ry = y + row * (mh + row_gap)
        cy = ry + (mh - 7 * 3) // 2
        s.text(nim.HEAPS[row], x, cy, 3, bold=True)
        for j in range(full):
            pal = PAL if j < size else {"#": "g", "Y": "g"}
            s.sprite(sprites.MATCH, x + 40 + j * pitch, ry, u, pal)
        by = ry + (mh - 7 * bit_u) // 2
        for i, bit in enumerate(format(size, f"0{width}b")):
            s.text(bit, bits_x + i * bit_pitch + 7 * bit_u // 2, by, bit_u,
                   "i" if bit == "1" else "m", bold=True, anchor="middle")
    y += 3 * mh + 2 * row_gap + 16
    total = nim.nim_sum(state["heaps"])
    rule = bits_width(bit_u, bit_pitch)
    s.rect(bits_x, y, rule, 4, "i")
    y += 4 + 16
    s.text("NIM-SUM", bits_x - 24, y + (7 * bit_u - 14) // 2, 2, "m", bold=True, anchor="end")
    for i, bit in enumerate(format(total, f"0{width}b")):
        bx = bits_x + i * bit_pitch
        if bit == "1":
            s.rect(bx - bit_u, y - bit_u, 7 * bit_u + 2 * bit_u, 9 * bit_u, "a")
        s.text(bit, bx + 7 * bit_u // 2, y, bit_u, "k" if bit == "1" else "m", bold=True,
               anchor="middle")
    return y + 7 * bit_u


def verdict(state: dict) -> str:
    return ("NOT 0: A WINNING MOVE EXISTS" if nim.nim_sum(state["heaps"])
            else "0: EVERY MOVE BREAKS IT")


def facts(state: dict) -> str:
    return f"GAME {state['game']} \u00b7 MOVE {state['move'] + 1}"


def last_move(state: dict, room: int) -> list[tuple[str, str, bool]]:
    """What just happened, as text runs on one line of `room`, the player's name shortened only
    if it has to be."""
    if not state["log"]:
        return [("NO MOVES YET. BE THE FIRST TO PLAY", "i", False)]
    e = state["log"][-1]
    label = ("LAST" if e["winner"] is None else f"GAME {e['game']}", "m", False)
    took = nim.describe(e["heap"], e["take"]).upper()
    rest = (" TOOK THE LAST MATCH. HUMANS WIN" if e["winner"] == "humans" else
            f" TOOK {took}, BOT TOOK " +
            ("THE LAST MATCH" if e["winner"] == "bot" else nim.describe(*e["bot"]).upper()))
    who = f"@{e['player']}"
    while len(who) > 2 and runs_width([label, (who + rest, "i", False)], 2) > room:
        who = who[:-1]
    return [label, (who + rest, "i", False)]


def log_indent(label: str) -> int:
    """Where the phone's last-move lines start, a space after their label."""
    return text_width(label, 2) + (SPACE_WIDTH + 2) * 2 if label else 0


def last_move_mobile(state: dict, room: int) -> tuple[str, list[str]]:
    """The phone's last move: a muted label, then a line per player beside it, so a login is
    shortened only if it overflows a line on its own."""
    if not state["log"]:
        return "", ["NO MOVES YET. BE THE FIRST TO PLAY"]
    e = state["log"][-1]
    label = "LAST" if e["winner"] is None else f"GAME {e['game']}"
    if e["winner"] == "bot":
        return label, ["WON BY THE BOT"]
    room -= log_indent(label)

    def fits(line: str) -> bool:
        return text_width(line, 2) <= room

    who = f"@{e['player']}"
    while not fits(who):
        who = who[:-1]
    if e["winner"] == "humans":
        won = f"WON BY {who}"
        return label, [won] if fits(won) else ["WON BY", who]
    took = nim.describe(e["heap"], e["take"]).upper()
    mine = f"{who} TOOK {took}"
    bot = f"BOT TOOK {nim.describe(*e['bot']).upper()}"
    return label, ([mine] if fits(mine) else [who, f"TOOK {took}"]) + [bot]


def bot_sprite(mood: str) -> list[str]:
    return sprites.BOT_SWEATING if mood == "sweating" else sprites.BOT


def board(state: dict, theme: str) -> str:
    top = 56 + 14 + 24  # the section label, then the card
    s = canvas(W, 0, board_alt(state), theme)
    s.css.extend([BLINK, *BOBBING])
    section_label(s, "PLAY", 56)
    mood = nim.bot_mood(state)
    x0, x1 = PAD, W - PAD

    y = top + 32
    s.text("NIM", x0, y, 3, bold=True)
    s.text(facts(state), x1, y + 4, 2, "m", anchor="end")
    s.text("TAKE THE LAST MATCH TO WIN", x0, y + 33, 2, "m")
    y += 47 + 28
    s.rect(x0, y, x1 - x0, 4, "g")

    # face-off: the humans, the score, the bot
    y += 4 + 32
    s.sprite(sprites.HUMAN, x0, y, 4, PAL, ' class="bob"')
    s.sprite(bot_sprite(mood), x1 - 64, y, 4, PAL, ' class="bob2"')
    s.text("HUMANS", x0 + 80, y + 10, 3, bold=True)
    s.text("YOUR MOVE", x0 + 80, y + 39, 2, "m")
    s.text("BOT", x1 - 80, y + 10, 3, bold=True, anchor="end")
    s.text(mood.upper(), x1 - 80, y + 39, 2, "m", anchor="end")
    side = 80 + max(text_width("HUMANS", 3, bold=True), text_width("YOUR MOVE", 2)) + 32
    score(s, state, W // 2, y, x1 - x0 - 2 * side, (6, 5, 4))
    y += 64 + 32
    s.rect(x0, y, x1 - x0, 4, "g")

    y += 4 + 32
    # the humans' matches on the left, the bot's working on the right, under each side's face
    bits_x = x1 - bits_width(4, 40)
    bottom = heaps(s, state, x0, y, 6, 56, 20, bits_x, 4, 40)
    s.text(verdict(state), bits_x - 24, bottom + 20, 2, "m", anchor="end")

    y = bottom + 20 + 14 + 32
    s.rect(x0, y, x1 - x0, 4, "g")
    y += 4 + 28
    runs(s, last_move(state, x1 - x0), x0, y, 2)
    y += 14 + 20
    your_move(s, x0, y - 1)
    s.text("YOUR MOVE: CLICK A KEY BELOW TO TAKE MATCHES", x0 + 28, y, 2)
    s.height = y + 14 + 28
    card(s, top)
    return s.render()


def board_mobile(state: dict) -> str:
    top = 40 + 14 + 20
    s = canvas(M, 0, board_alt(state), "auto")
    s.css.extend([BLINK, *BOBBING])
    section_label(s, "PLAY", 40)
    mood = nim.bot_mood(state)
    x0, x1 = MPAD, M - MPAD
    mid = M // 2

    y = top + 20
    s.text("NIM", x0, y, 3, bold=True)
    s.text(facts(state), x1, y + 4, 2, "m", anchor="end")
    y += 21 + 12
    s.text("TAKE THE LAST MATCH TO WIN", x0, y, 2, "m")
    y += 14 + 18
    s.rect(x0, y, x1 - x0, 4, "g")

    y += 4 + 20
    s.sprite(sprites.HUMAN, x0 - 4, y, 4, PAL, ' class="bob"')
    s.sprite(bot_sprite(mood), x1 - 60, y, 4, PAL, ' class="bob2"')
    score(s, state, mid, y, x1 - x0 - 152, (5, 4, 3))
    s.text("HUMANS", x0, y + 76, 2, bold=True)
    s.text("BOT", x1, y + 76, 2, bold=True, anchor="end")
    s.text("YOUR MOVE", x0, y + 98, 2, "m")
    s.text(mood.upper(), x1, y + 98, 2, "m", anchor="end")
    y += 112 + 16
    s.rect(x0, y, x1 - x0, 4, "g")

    y += 4 + 20
    bits_x = x1 - bits_width(3, 28)
    bottom = heaps(s, state, x0 + 4, y, 3, 26, 14, bits_x, 3, 28)
    y = bottom + 16
    s.text(verdict(state), x1, y, 2, "m", anchor="end")
    y += 14 + 20
    s.rect(x0, y, x1 - x0, 4, "g")
    y += 4 + 20
    label, lines = last_move_mobile(state, x1 - x0)
    if label:
        s.text(label, x0, y, 2, "m")
    for i, line in enumerate(lines):
        s.text(line, x0 + log_indent(label), y + 24 * i, 2)
    y += 24 * (len(lines) - 1) + 14 + 16
    your_move(s, x0, y - 1)
    s.text("TAP A KEY BELOW TO TAKE MATCHES", x0 + 28, y, 2)
    s.height = y + 14 + 20
    card(s, top)
    return s.render()


def board_alt(state: dict) -> str:
    a, b, c = state["heaps"]
    return (
        f"Nim against a perfect bot, game {state['game']}, move {state['move'] + 1}. "
        f"Heaps: A has {a}, B has {b}, C has {c}; nim-sum {nim.nim_sum(state['heaps'])}. "
        f"Games won: humans {state['wins']['humans']}, bot {state['wins']['bot']}. "
        f"{last_move_alt(state)} Pick a heap and how many matches to take with the keys below."
    )


def last_move_alt(state: dict) -> str:
    if not state["log"]:
        return "No moves yet."
    e = state["log"][-1]
    took = f"@{e['player']} took {nim.describe(e['heap'], e['take'])}"
    if e["winner"] == "humans":
        return f"Game {e['game']}: @{e['player']} took the last match, so humans won."
    if e["winner"] == "bot":
        return f"Game {e['game']}: {took}, then the bot took the last match and won."
    return f"Last move: {took}, then the bot took {nim.describe(*e['bot'])}."


# ----------------------------------------------------------------------------- keypad

def keycap(label: str, theme: str, width: int, *, top: int, h: int, side: int, u: int) -> str:
    """One key of the keypad under the board, with an 8px gutter between neighbours."""
    s = canvas(width, top + h, label.capitalize(), theme)
    x, w = 4, width - 8
    fx, fy, fw, fh = x + 4, top + 4, w - 8, h - 8 - side
    s.path(notched(x, top, w, h, 4), "i")
    s.path(notched(fx, fy, fw, h - 8, 3), "o")  # the key's side
    s.path(notched(fx, fy, fw, fh, 3), "a")
    s.text(label, fx + fw / 2, fy + (fh - 7 * u) / 2, u, "k", bold=True, anchor="middle")
    return s.render()


def take_key(n: int, theme: str) -> str:
    return keycap(f"TAKE {n}", theme, KEY_W, top=8, h=56, side=8, u=3)


def take_key_mobile(n: int) -> str:
    return keycap(str(n), "auto", KEY_M, top=8, h=60, side=8, u=4)


def row_label(text: str, theme: str, width: int, *, top: int, h: int, side: int, u: int,
              cls: str = "i", bold: bool = True) -> str:
    """The text in a keypad row that isn't a key: the heap's name, or EMPTY."""
    s = canvas(width, top + h, text.capitalize(), theme)
    s.text(text, 4, top + 4 + (h - 8 - side - 7 * u) / 2, u, cls, bold=bold)
    return s.render()


def heap_label(heap: int, theme: str) -> str:
    return row_label(f"HEAP {nim.HEAPS[heap]}", theme, KEY_W, top=8, h=56, side=8, u=3)


def heap_label_mobile(heap: int) -> str:
    return row_label(nim.HEAPS[heap], "auto", KEY_M, top=8, h=60, side=8, u=4)


def empty(theme: str) -> str:
    return row_label("EMPTY", theme, KEY_W, top=8, h=56, side=8, u=3, cls="m", bold=False)


def empty_mobile() -> str:
    return row_label("EMPTY", "auto", KEY_M, top=8, h=60, side=8, u=2, cls="m", bold=False)


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
    y = 56  # with the 8px under the hero, the same 64px that sits above every section label
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
    y = 40  # 48px above every section label on phones
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
