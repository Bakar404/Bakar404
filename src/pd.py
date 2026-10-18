"""Prisoner's Dilemma vs. the bot: pure game logic, no I/O.

The bot commits to its move from history alone, before it reads yours:
  * first time you play, it treats you the way the previous player treated it;
  * after that it plays tit-for-tat with you (it repeats your last move).
"""
from __future__ import annotations

import re

COOPERATE, DEFECT = "C", "D"
WORD = {COOPERATE: "cooperate", DEFECT: "defect"}
PAST = {COOPERATE: "cooperated", DEFECT: "defected"}
# (human points, bot points); the classic Axelrod payoffs T=5 > R=3 > P=1 > S=0.
PAYOFFS = {
    (COOPERATE, COOPERATE): (3, 3),
    (COOPERATE, DEFECT): (0, 5),
    (DEFECT, COOPERATE): (5, 0),
    (DEFECT, DEFECT): (1, 1),
}
HISTORY_LIMIT = 60

_PREFIX = re.compile(r"^\s*pd\s*:", re.IGNORECASE)
_MOVE = re.compile(r"^\s*pd\s*:\s*(cooperate|defect)\s*$", re.IGNORECASE)
_LOGIN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")


def new_state() -> dict:
    return {
        "round": 0,
        "last_issue": 0,
        "totals": {"humans": 0, "bot": 0},
        "outcomes": {"CC": 0, "CD": 0, "DC": 0, "DD": 0},
        "last_human_move": None,
        "players": {},
        "history": [],
    }


def is_game_issue(title: str | None) -> bool:
    return bool(_PREFIX.match(title or ""))


def parse_move(title: str | None) -> str | None:
    match = _MOVE.match(title or "")
    if not match:
        return None
    return COOPERATE if match.group(1).lower() == "cooperate" else DEFECT


def valid_login(login: str | None) -> bool:
    return bool(_LOGIN.match(login or ""))


def bot_move(state: dict, player: str) -> tuple[str, str]:
    """Return (move, reason) using only what happened before this round."""
    record = state["players"].get(player)
    if record:
        return record["last"], "tit-for-tat"
    if state["last_human_move"]:
        return state["last_human_move"], "stranger"
    return COOPERATE, "opening"


def play(state: dict, player: str, move: str, issue: int, at: str) -> dict:
    """Resolve one round in place and return its history entry."""
    if move not in (COOPERATE, DEFECT):
        raise ValueError(f"unknown move {move!r}")
    bot, reason = bot_move(state, player)
    human_points, bot_points = PAYOFFS[(move, bot)]

    state["round"] += 1
    state["totals"]["humans"] += human_points
    state["totals"]["bot"] += bot_points
    state["outcomes"][move + bot] += 1
    state["last_human_move"] = move
    state["last_issue"] = max(state["last_issue"], issue)

    record = state["players"].setdefault(player, {"last": move, "rounds": 0, "points": 0})
    record["last"] = move
    record["rounds"] += 1
    record["points"] += human_points

    entry = {
        "round": state["round"], "player": player, "human": move, "bot": bot,
        "reason": reason, "issue": issue, "at": at,
    }
    state["history"] = (state["history"] + [entry])[-HISTORY_LIMIT:]
    return entry


def cooperation_rate(state: dict) -> int:
    """Share of human moves that were cooperative, as a whole percent."""
    if not state["round"]:
        return 0
    cooperative = state["outcomes"]["CC"] + state["outcomes"]["CD"]
    return round(100 * cooperative / state["round"])


def bot_mood(state: dict) -> str:
    """How the bot will greet the next newcomer."""
    return "suspicious" if state["last_human_move"] == DEFECT else "trusting"


def reply(entry: dict, state: dict, board_url: str) -> str:
    """Markdown comment explaining the round to the player."""
    you, bot = entry["human"], entry["bot"]
    human_points, bot_points = PAYOFFS[(you, bot)]
    why = {
        "opening": "You're the very first player, so the bot opened by cooperating.",
        "stranger": (
            "First game? The bot treats newcomers the way it was last treated, "
            f"and the previous player **{PAST[bot]}**."
        ),
        "tit-for-tat": (
            f"You've played before, so the bot repeated your last move (**{WORD[bot]}**). "
            "That's tit-for-tat."
        ),
    }[entry["reason"]]
    record = state["players"].get(entry["player"], {"rounds": 1, "points": human_points})
    cells = {key: f"{a}, {b}" for key, (a, b) in PAYOFFS.items()}
    cells[(you, bot)] = f"**{cells[(you, bot)]}** (this round)"
    mood = "trusting" if you == COOPERATE else "suspicious"
    return (
        f"**Round {entry['round']}:** you **{PAST[you]}**, the bot **{PAST[bot]}**. "
        f"You +{human_points}, bot +{bot_points}.\n\n"
        f"{why}\n\n"
        f"Your move also set the bot's mood for the next newcomer: **{mood}**.\n\n"
        "| you \\ bot | cooperate | defect |\n|---|---|---|\n"
        f"| **cooperate** | {cells[('C', 'C')]} | {cells[('C', 'D')]} |\n"
        f"| **defect** | {cells[('D', 'C')]} | {cells[('D', 'D')]} |\n\n"
        f"Your record: {record['rounds']} round(s), {record['points']} point(s). "
        f"See the board at {board_url} (it can take a few minutes to refresh)."
    )


def invalid_reply(board_url: str) -> str:
    return (
        "I couldn't read a move from this title. Use the buttons on the board "
        f"({board_url}) or title an issue exactly `pd: cooperate` or `pd: defect`."
    )
