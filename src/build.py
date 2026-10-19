"""Render every asset and the README around them.

    python3 src/build.py           # all assets, and README.md from the template below
    python3 src/build.py --board   # only the game: board and keys (what the Action runs)

README.md is generated: edit the template here, not the file.

Every image is a <picture>. Phones (PHONE) get their own layout, which picks its own colours;
everywhere else gets a light or dark version through prefers-color-scheme. GitHub rewrites the
colour-scheme queries when someone forces a theme, and leaves the width query alone.
"""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlencode

import nim
import scenes

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
STATE = ROOT / "data" / "nim.json"
README = ROOT / "README.md"
THEMES = ("light", "dark")
REPO = "Bakar404/Bakar404"
PHONE = "(max-width: 600px)"
GAME = re.compile(r"<!-- game -->\n.*?\n<!-- /game -->", re.S)
SIZE = re.compile(r'<svg [^>]*width="(\d+)"')

# The page is one raw HTML block, so Markdown's line-break rules never touch it. The game sits
# last, so visitors meet Ahmed before they get absorbed in it; the Action rewrites only the part
# between the game markers.
TEMPLATE = """\
<p>
{hero}<br>
{specs}<br>
{game}
</p>

<details>
<summary>{summary}</summary>
<br>

The bot never guesses. It writes each heap in binary and XORs them together, column by column with no carrying. That's the **nim-sum**.

- **Facing a nim-sum of 0?** Any move you make breaks the zero, and the bot can always restore it. It keeps handing you zeros until it takes the last match.
- **Facing anything else?** Some move turns it into 0. Make that move every turn and you take the last match. Charles L. Bouton proved this in 1901, one of the first results in [combinatorial game theory](https://en.wikipedia.org/wiki/Nim).

Every game starts with a nonzero nim-sum and you move first, so a perfect bot can still be beaten.

A key opens an issue titled like `nim: take 2 from A (game 1, move 1)`. A [GitHub Action](.github/workflows/nim.yml) plays your move and the bot's with [`src/nim.py`](src/nim.py), redraws the board and replies to you. Every pixel here is drawn by [`src/scenes.py`](src/scenes.py).

</details>
"""


def load_state() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else nim.new_state()


def save_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=1) + "\n")


def picture(name: str, alt: str, width: int, query: str = "", align: bool = True) -> str:
    """An image sized in percent of the README, so every scene scales together."""
    q = f"?{query}" if query else ""
    pct = f"{int(width / scenes.W * 100_000) / 1000:g}%"  # rounded down: rows must not wrap
    return (
        "<picture>"
        f'<source media="{PHONE}" srcset="assets/{name}-phone.svg{q}">'
        f'<source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg{q}">'
        f'<img alt="{html.escape(alt)}" src="assets/{name}-light.svg{q}" width="{pct}"'
        + (' align="top"' if align else "")
        + "></picture>"
    )


def board_picture(state: dict) -> str:
    # The query string changes every move so GitHub's image cache can't serve a stale board.
    return picture("board", scenes.board_alt(state), scenes.W,
                   f"v={state['game']}-{state['move']}")


def issue_url(state: dict, heap: int, take: int) -> str:
    return f"https://github.com/{REPO}/issues/new?" + urlencode({
        "title": nim.title(heap, take, state["game"], state["move"] + 1),
        "body": "Submit this issue to make your move. The bot answers, redraws the board on "
                f"github.com/{REPO.split('/')[0]} and replies here in about a minute."
                "\n\nPlease keep the title as it is.",
    })


def keypad(state: dict) -> str:
    """One row per heap: its name, then a key for every legal number of matches to take."""
    rows = []
    for heap, size in enumerate(state["heaps"]):
        name = nim.HEAPS[heap]
        cells = [picture(f"heap-{name.lower()}", f"Heap {name}:", scenes.KEY_W)]
        cells += [
            f'<a href="{html.escape(issue_url(state, heap, take))}">'
            + picture(f"take-{take}", f"Take {take} from heap {name}", scenes.KEY_W) + "</a>"
            for take in range(1, size + 1)
        ] or [picture("empty", "empty", scenes.KEY_W)]
        rows.append("".join(cells))
    return "<br>\n".join(rows)


def game(state: dict) -> str:
    return f"<!-- game -->\n{board_picture(state)}<br>\n{keypad(state)}\n<!-- /game -->"


def write_board(state: dict, readme: Path | None = None) -> None:
    readme = readme or README
    ASSETS.mkdir(exist_ok=True)
    for theme in THEMES:
        (ASSETS / f"board-{theme}.svg").write_text(scenes.board(state, theme))
    (ASSETS / "board-phone.svg").write_text(scenes.board_mobile(state))
    text, found = GAME.subn(lambda _: game(state), readme.read_text())
    if found != 1:
        raise SystemExit("README.md needs exactly one game block")
    readme.write_text(text)


# name: (desktop scene, phone scene)
STATIC = {
    "hero": (scenes.hero, scenes.hero_mobile),
    "specs": (scenes.specs, scenes.specs_mobile),
    **{f"heap-{name.lower()}": (lambda theme, i=i: scenes.heap_label(i, theme),
                                lambda i=i: scenes.heap_label_mobile(i))
       for i, name in enumerate(nim.HEAPS)},
    **{f"take-{n}": (lambda theme, n=n: scenes.take_key(n, theme),
                     lambda n=n: scenes.take_key_mobile(n))
       for n in range(1, nim.MAX_HEAP + 1)},
    "empty": (scenes.empty, scenes.empty_mobile),
    "summary": (scenes.summary, scenes.summary_mobile),
}


def write_static() -> dict[str, int]:
    """Write the scenes that never change; returns each one's desktop width."""
    ASSETS.mkdir(exist_ok=True)
    widths = {}
    for name, (desktop, phone) in STATIC.items():
        for theme in THEMES:
            svg = desktop(theme)
            (ASSETS / f"{name}-{theme}.svg").write_text(svg)
        widths[name] = int(SIZE.search(svg).group(1))
        (ASSETS / f"{name}-phone.svg").write_text(phone())
    return widths


def write_readme(state: dict, widths: dict[str, int]) -> None:
    README.write_text(TEMPLATE.format(
        hero=picture("hero", scenes.hero_alt(), widths["hero"]),
        specs=picture("specs", scenes.specs_alt(), widths["specs"]),
        game=game(state),
        summary=picture("summary", scenes.SUMMARY, widths["summary"], align=False),
    ))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--board", action="store_true", help="only re-render the game")
    args = parser.parse_args()
    state = load_state()
    if not args.board:
        write_readme(state, write_static())
    write_board(state)


if __name__ == "__main__":
    main()
