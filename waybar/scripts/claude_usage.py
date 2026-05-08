#!/usr/bin/env python3
"""Waybar custom module: Claude Code usage from ~/.claude/projects/ JSONL files."""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude" / "projects"


def load_usage():
    now = datetime.now(timezone.utc)
    cutoff_5h = now - timedelta(hours=5)
    cutoff_7d = now - timedelta(days=7)

    tokens_5h = 0
    tokens_7d = 0

    for jsonl in PROJECTS_DIR.rglob("*.jsonl"):
        try:
            with open(jsonl) as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if entry.get("type") != "assistant":
                        continue

                    msg = entry.get("message", {})
                    # Only count final responses, not streaming chunks
                    if not msg.get("stop_reason"):
                        continue

                    usage = msg.get("usage", {})
                    out = usage.get("output_tokens", 0)
                    if not out:
                        continue

                    ts_str = entry.get("timestamp", "")
                    try:
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    except (ValueError, AttributeError):
                        continue

                    if ts >= cutoff_7d:
                        tokens_7d += out
                    if ts >= cutoff_5h:
                        tokens_5h += out
        except OSError:
            continue

    return tokens_5h, tokens_7d


def fmt(n):
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def main():
    t5h, t7d = load_usage()

    text = f"󰚩 {fmt(t5h)}"
    tooltip = (
        f"Claude Code Usage\n"
        f"Session (5h):  {t5h:,} tokens\n"
        f"Last 7 days:   {t7d:,} tokens"
    )

    # Visual hint: dim = plenty of room, normal = moderate, warning = heavy use
    if t5h < 20_000:
        css_class = "low"
    elif t5h < 60_000:
        css_class = "medium"
    else:
        css_class = "high"

    print(json.dumps({"text": text, "tooltip": tooltip, "class": css_class}))


if __name__ == "__main__":
    main()
