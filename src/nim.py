"""Nim vs. the bot: pure game logic, no I/O.

Three heaps of matches. Each turn a player takes one or more matches from a single heap, and
whoever takes the last match wins. Visitors play together as the humans and always move
first; the bot answers every move.

The bot plays perfectly. XOR the heap sizes together to get the nim-sum: from a nonzero
nim-sum there is always a move back to zero, and from zero every move leaves it nonzero
(Bouton, 1901). The bot keeps handing the humans a zero. Every game starts nonzero, so humans
who find the right moves can beat it.
"""
from __future__ import annotations

import re
from functools import reduce

HEAPS = "ABC"
# Every start has a nonzero nim-sum, so the side moving first (the visitors) can win.
STARTS = [(3, 4, 5), (1, 3, 5), (2, 4, 5), (2, 3, 5), (3, 5, 5)]
MAX_HEAP = max(max(start) for start in STARTS)
LOG_LIMIT = 60
RESULTS_LIMIT = 20

_PREFIX = re.compile(r"^\s*nim\s*:", re.IGNORECASE)
_MOVE = re.compile(
    r"^\s*nim\s*:\s*take\s+(\d+)\s+from\s+([abc])\s*\(\s*game\s+(\d+)\s*,\s*move\s+(\d+)\s*\)\s*$",
    re.IGNORECASE,
)
_LOGIN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")


def new_state() -> dict:
    return {
        "game": 1,
        "move": 0,  # visitor moves already made in this game
        "heaps": list(STARTS[0]),
        "wins": {"humans": 0, "bot": 0},
        "players": {},
        "last_issue": 0,
        "log": [],
        "results": [],
    }


def nim_sum(heaps: list[int] | tuple[int, ...]) -> int:
    return reduce(lambda a, b: a ^ b, heaps, 0)


def title(heap: int, take: int, game: int, move: int) -> str:
    return f"nim: take {take} from {HEAPS[heap]} (game {game}, move {move})"


def is_game_issue(text: str | None) -> bool:
    return bool(_PREFIX.match(text or ""))


def parse_move(text: str | None) -> dict | None:
    match = _MOVE.match(text or "")
    if not match:
        return None
    take, heap, game, move = match.groups()
    return {"heap": HEAPS.index(heap.upper()), "take": int(take), "game": int(game),
            "move": int(move)}


def valid_login(login: str | None) -> bool:
    return bool(_LOGIN.match(login or ""))


def check(state: dict, move: dict) -> str | None:
    """Why a parsed move can't be played right now, or None if it can."""
    if (move["game"], move["move"]) != (state["game"], state["move"] + 1):
        return "stale"
    if not 1 <= move["take"] <= state["heaps"][move["heap"]]:
        return "illegal"
    return None


def bot_move(heaps: list[int]) -> tuple[int, int]:
    """(heap, take) that leaves a nim-sum of zero, or a single match when no move can."""
    total = nim_sum(heaps)
    if total:
        for heap, size in enumerate(heaps):
            if size ^ total < size:
                return heap, size - (size ^ total)
    heap = max(range(len(heaps)), key=lambda i: heaps[i])
    return heap, 1


def bot_mood(state: dict) -> str:
    """The bot can read the board too: a nonzero nim-sum means visitors can win."""
    return "sweating" if nim_sum(state["heaps"]) else "calm"


def play(state: dict, player: str, heap: int, take: int, issue: int, at: str) -> dict:
    """Make the visitors' move and the bot's answer in place. Returns the log entry."""
    if not 1 <= take <= state["heaps"][heap]:
        raise ValueError(f"can't take {take} from heap {HEAPS[heap]}")
    entry = {
        "issue": issue, "player": player, "game": state["game"], "move": state["move"] + 1,
        "heap": heap, "take": take, "bot": None, "winner": None, "at": at,
    }
    state["heaps"][heap] -= take
    state["move"] += 1
    state["last_issue"] = max(state["last_issue"], issue)
    state["players"][player] = state["players"].get(player, 0) + 1

    if not any(state["heaps"]):
        entry["winner"] = "humans"
    else:
        bot_heap, bot_take = bot_move(state["heaps"])
        state["heaps"][bot_heap] -= bot_take
        entry["bot"] = [bot_heap, bot_take]
        if not any(state["heaps"]):
            entry["winner"] = "bot"
    entry["heaps"] = list(state["heaps"])

    if entry["winner"]:
        state["wins"][entry["winner"]] += 1
        state["results"] = (state["results"] + [{
            "game": state["game"], "winner": entry["winner"], "moves": state["move"],
            "player": player,
        }])[-RESULTS_LIMIT:]
        state["game"] += 1
        state["move"] = 0
        state["heaps"] = list(STARTS[(state["game"] - 1) % len(STARTS)])
    state["log"] = (state["log"] + [entry])[-LOG_LIMIT:]
    return entry


def describe(heap: int, take: int) -> str:
    return f"{take} from {HEAPS[heap]}"


def sticks(heaps: list[int]) -> str:
    """The position as a code block, one heap per line."""
    lines = [f"{HEAPS[i]}  {' '.join('|' * size) or '(empty)'}" for i, size in enumerate(heaps)]
    return "```\n" + "\n".join(lines) + "\n```"


def reply(entry: dict, state: dict, board_url: str) -> str:
    """Markdown comment telling the player what happened."""
    you = f"You took **{describe(entry['heap'], entry['take'])}**"
    score = f"Games won: humans {state['wins']['humans']}, bot {state['wins']['bot']}."
    if entry["winner"] == "humans":
        return (
            f"{you}, emptying the board. **Humans win game {entry['game']}!** The bot plays "
            "perfectly, so the humans before you must have handed it a nim-sum of 0 every "
            f"single turn.\n\n{score} Game {state['game']} is already on the board: {board_url}"
        )
    bot = f"the bot took **{describe(*entry['bot'])}**"
    if entry["winner"] == "bot":
        return (
            f"{you}, then {bot}, emptying the board. **The bot wins game {entry['game']}.**\n\n"
            f"{score} Game {state['game']} is already on the board, and it opens with a "
            f"winning move for whoever finds it: {board_url}"
        )
    after = entry["heaps"]
    total = nim_sum(after)
    if total:
        verdict = (
            f"The nim-sum (XOR of the heaps) is **{total}**, not 0, so there is a winning move "
            "from here and the bot is sweating. Can the next human find it?"
        )
    else:
        verdict = (
            "The nim-sum (XOR of the heaps) is back to **0**. That's where the bot wants you: "
            "every move breaks the zero, and it can always restore it."
        )
    return (
        f"**Game {entry['game']}, move {entry['move']}.** {you}, then {bot}.\n\n"
        f"{sticks(after)}\n\n{verdict}\n\n"
        f"The board on {board_url} shows the new position (it can take a few minutes to refresh)."
    )


def rejection(reason: str, state: dict, board_url: str) -> str:
    if reason == "stale":
        return (
            "Someone moved first, so this move was made on an old board. Here is the position "
            f"now:\n\n{sticks(state['heaps'])}\n\nPick your move again from the board on "
            f"{board_url}"
        )
    if reason == "illegal":
        return (
            "That heap doesn't have that many matches left. Pick your move again from the "
            f"board on {board_url}"
        )
    return (
        "I couldn't read a move from this title. Use the keys under the board on "
        f"{board_url}, which fill it in for you."
    )
