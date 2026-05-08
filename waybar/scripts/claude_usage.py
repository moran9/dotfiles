#!/usr/bin/env python3
"""Waybar custom module: Claude Code usage from ~/.claude/projects/ JSONL files."""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude" / "projects"

# Output token limit for your Claude Code plan per 5h window.
# Pro ≈ 88_000 · Max 5x ≈ 440_000 · Max 20x ≈ 1_760_000
LIMIT_5H = 88_000


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

    pct_5h = min(round(t5h / LIMIT_5H * 100), 100)
    pct_7d = min(round(t7d / (LIMIT_5H * 7 * 24 / 5) * 100), 100)
    text = f"󰚩 {pct_5h}% · {pct_7d}%"
    tooltip = (
        f"Claude Code Usage\n"
        f"Session (5h):  {pct_5h}% · {t5h:,} / {LIMIT_5H:,} tokens\n"
        f"Last 7 days:   {pct_7d}% · {t7d:,} tokens"
    )

    if pct_5h < 40:
        css_class = "low"
    elif pct_5h < 75:
        css_class = "medium"
    else:
        css_class = "high"

    print(json.dumps({"text": text, "tooltip": tooltip, "class": css_class}))


if __name__ == "__main__":
    main()
