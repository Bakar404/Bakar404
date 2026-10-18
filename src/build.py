"""Render every asset and the README around them.

    python3 src/build.py           # all assets, and README.md from the template below
    python3 src/build.py --board   # only the board (what the Action runs after each round)

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

import pd
import scenes

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
STATE = ROOT / "data" / "pd.json"
README = ROOT / "README.md"
THEMES = ("light", "dark")
REPO = "Bakar404/Bakar404"
PHONE = "(max-width: 600px)"
BOARD_PICTURE = re.compile(r'<picture><source [^>]*assets/board-[^>]*>.*?</picture>', re.S)
SIZE = re.compile(r'<svg [^>]*width="(\d+)"')

# The header is one raw HTML block, so Markdown's line-break rules never touch it.
TEMPLATE = """\
<p>
{name}<br>
{tagline}<br>
{board}<br>
<a href="{cooperate_url}">{cooperate}</a><a href="{defect_url}">{defect}</a>
</p>

<details>
<summary>{summary}</summary>
<br>

The bot locks in its move before it reads yours.

- **First time playing?** It treats you the way the last player treated it.
- **Played before?** It repeats your previous move. That's [tit-for-tat](https://en.wikipedia.org/wiki/Tit_for_tat), the strategy that won Robert Axelrod's 1980 tournament.

| you \\ bot | cooperate | defect |
| --- | --- | --- |
| **cooperate** | 3, 3 | 0, 5 |
| **defect** | 5, 0 | 1, 1 |

A button opens an issue titled `pd: cooperate` or `pd: defect`. A [GitHub Action](.github/workflows/prisoners-dilemma.yml) plays the round with [`src/pd.py`](src/pd.py), redraws the board and replies to you. Every pixel here is drawn by [`src/scenes.py`](src/scenes.py).

</details>

{specs}
"""


def load_state() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else pd.new_state()


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
    # The query string changes every round so GitHub's image cache can't serve a stale board.
    return picture("board", scenes.board_alt(state), scenes.W, f"r={state['round']}")


def issue_url(move: str) -> str:
    return f"https://github.com/{REPO}/issues/new?" + urlencode({
        "title": f"pd: {move}",
        "body": "Submit this issue to lock in your move. The bot plays the round, redraws the "
                f"board on github.com/{REPO.split('/')[0]} and replies here in about a minute."
                "\n\nPlease keep the title as it is.",
    })


def write_board(state: dict, readme: Path | None = None) -> None:
    readme = readme or README
    ASSETS.mkdir(exist_ok=True)
    for theme in THEMES:
        (ASSETS / f"board-{theme}.svg").write_text(scenes.board(state, theme))
    (ASSETS / "board-phone.svg").write_text(scenes.board_mobile(state))
    snippet = board_picture(state)
    text, found = BOARD_PICTURE.subn(lambda _: snippet, readme.read_text())
    if found != 1:
        raise SystemExit("README.md needs exactly one board <picture>")
    readme.write_text(text)


# name: (desktop scene, phone scene)
STATIC = {
    "name": (scenes.name, scenes.name_mobile),
    "tagline": (scenes.tagline, scenes.tagline_mobile),
    "btn-cooperate": (lambda theme: scenes.button("C", theme), lambda: scenes.button_mobile("C")),
    "btn-defect": (lambda theme: scenes.button("D", theme), lambda: scenes.button_mobile("D")),
    "summary": (scenes.summary, scenes.summary_mobile),
    "specs": (scenes.specs, scenes.specs_mobile),
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
        name=picture("name", scenes.NAME, widths["name"]),
        tagline=picture("tagline", scenes.TAGLINE, widths["tagline"]),
        board=board_picture(state),
        cooperate=picture("btn-cooperate", "Cooperate", widths["btn-cooperate"]),
        defect=picture("btn-defect", "Defect", widths["btn-defect"]),
        cooperate_url=html.escape(issue_url("cooperate")),
        defect_url=html.escape(issue_url("defect")),
        summary=picture("summary", scenes.SUMMARY, widths["summary"], align=False),
        specs=picture("specs", scenes.specs_alt(), widths["specs"]),
    ))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--board", action="store_true", help="only re-render the board")
    args = parser.parse_args()
    state = load_state()
    if not args.board:
        write_readme(state, write_static())
    write_board(state)


if __name__ == "__main__":
    main()
