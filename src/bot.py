"""GitHub Action entry point for the Prisoner's Dilemma board.

    python3 src/bot.py play  --plan PLAN.json   # play open `pd:` issues, redraw the board
    python3 src/bot.py reply --plan PLAN.json   # comment on and close those issues

The workflow runs `play`, commits and pushes, then runs `reply`, so a player is only
told about a round once it is on the board. Each run drains *every* open move, which
keeps the game correct even when GitHub drops queued runs.

For local testing: `--issues-file issues.json` replaces the API read and `--dry-run`
prints replies instead of posting them.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

import build
import pd

API = "https://api.github.com"


def api(method: str, path: str, body: dict | None = None):
    request = urllib.request.Request(
        API + path,
        data=None if body is None else json.dumps(body).encode(),
        method=method,
        headers={
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "prisoners-dilemma-bot",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
    return json.loads(raw) if raw else None


def open_game_issues(repo: str) -> list[dict]:
    issues = []
    for page in range(1, 6):
        batch = api("GET", f"/repos/{repo}/issues?state=open&sort=created&direction=asc"
                           f"&per_page=100&page={page}")
        issues += batch
        if len(batch) < 100:
            break
    return issues


def play(issues: list[dict], board_url: str) -> list[dict]:
    """Resolve every pending move in issue order. Returns the replies to post."""
    state = build.load_state()
    played = {entry["issue"]: entry for entry in state["history"]}
    replies, changed = [], False
    for issue in sorted(issues, key=lambda i: i["number"]):
        if "pull_request" in issue or not pd.is_game_issue(issue["title"]):
            continue
        number, login = issue["number"], issue["user"]["login"]
        entry = played.get(number)
        if entry:
            # Already on the board; an earlier run must have failed before replying.
            replies.append({"issue": number, "body": pd.reply(entry, state, board_url),
                            "reason": "completed"})
            continue
        move = pd.parse_move(issue["title"])
        if move is None or not pd.valid_login(login):
            replies.append({"issue": number, "body": pd.invalid_reply(board_url),
                            "reason": "not_planned"})
            continue
        entry = pd.play(state, login, move, number, issue["created_at"])
        replies.append({"issue": number, "body": pd.reply(entry, state, board_url),
                        "reason": "completed"})
        changed = True
    if changed:
        build.save_state(state)
        build.write_board(state)
    return replies


def reply(replies: list[dict], repo: str, dry_run: bool) -> int:
    failures = 0
    for r in replies:
        if dry_run:
            print(f"--- #{r['issue']} ({r['reason']})\n{r['body']}\n")
            continue
        try:
            api("POST", f"/repos/{repo}/issues/{r['issue']}/comments", {"body": r["body"]})
            api("PATCH", f"/repos/{repo}/issues/{r['issue']}",
                {"state": "closed", "state_reason": r["reason"]})
        except Exception as error:  # keep going so one bad issue can't block the rest
            failures += 1
            print(f"could not reply to #{r['issue']}: {error}", file=sys.stderr)
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Prisoner's Dilemma bot")
    parser.add_argument("command", choices=("play", "reply"))
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--issues-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo = os.environ.get("GITHUB_REPOSITORY", "Bakar404/Bakar404")
    board_url = f"https://github.com/{repo.split('/')[0]}"
    if args.command == "play":
        issues = (json.loads(args.issues_file.read_text()) if args.issues_file
                  else open_game_issues(repo))
        replies = play(issues, board_url)
        args.plan.write_text(json.dumps(replies, indent=1))
        print(f"{len(replies)} issue(s) to answer")
        return 0
    return reply(json.loads(args.plan.read_text()), repo, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
