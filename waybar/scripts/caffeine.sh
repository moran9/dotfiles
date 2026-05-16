#!/usr/bin/env bash
# Caffeine for Hyprland: stops hypridle from auto-locking / suspending.
#
#   caffeine.sh           emit waybar JSON state
#   caffeine.sh toggle    flip on/off (and notify)
#
# Implementation: "caffeine ON" simply means hypridle is not running.
# Toggling kills or respawns the idle daemon. Plays nicely with the
# waybar custom module that polls this script every few seconds.

set -euo pipefail

cmd="${1:-status}"

# Coffee glyph (FontAwesome  — present in Nerd Fonts).
ICON=$''

is_caffeinated() {
    ! pgrep -x hypridle >/dev/null 2>&1
}

case "$cmd" in
    toggle)
        if is_caffeinated; then
            # Restore idle daemon → caffeine OFF.
            setsid -f hypridle >/dev/null 2>&1 || hypridle >/dev/null 2>&1 &
            notify-send -a caffeine "caffeine off" "auto-lock and sleep re-enabled"
        else
            pkill -x hypridle 2>/dev/null || true
            notify-send -a caffeine "caffeine ON" "system will not auto-lock or sleep"
        fi
        ;;
    status|*)
        if is_caffeinated; then
            printf '{"text":"%s","class":"on","tooltip":"caffeine ON — sleep inhibited"}\n' "$ICON"
        else
            printf '{"text":"%s","class":"off","tooltip":"caffeine off (idle daemon active)"}\n' "$ICON"
        fi
        ;;
esac
