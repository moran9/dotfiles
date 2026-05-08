#!/usr/bin/env bash
# apply.sh — Copy configs from the dotfiles repo to ~/.config and reload each utility.
# Usage:
#   ./apply.sh          # apply all utilities
#   ./apply.sh hypr     # apply only hypr
#   ./apply.sh waybar   # apply only waybar

set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── per-utility handlers ────────────────────────────────────────────────────

apply_hypr() {
    local dest="$HOME/.config/hypr"
    mkdir -p "$dest"
    cp -r "$DOTFILES_DIR/hypr/." "$dest/"
    # Hyprland is the running session; reload instead of restart
    hyprctl reload
    echo "  hypr: config applied and reloaded"
}

apply_waybar() {
    local dest="$HOME/.config/waybar"
    mkdir -p "$dest"
    cp -r "$DOTFILES_DIR/waybar/." "$dest/"
    chmod +x "$dest/scripts/"*.py 2>/dev/null || true
    pkill -x waybar 2>/dev/null || true
    sleep 0.3
    waybar >/dev/null 2>&1 &
    disown $!
    echo "  waybar: config applied and restarted"
}

# ── dispatch ────────────────────────────────────────────────────────────────

ALL_UTILITIES=(hypr waybar)
targets=("${@:-${ALL_UTILITIES[@]}}")

for util in "${targets[@]}"; do
    dir="$DOTFILES_DIR/$util"

    if [[ ! -d "$dir" ]]; then
        echo "  $util: directory not found, skipping"
        continue
    fi

    # Skip empty directories
    if [[ -z "$(ls -A "$dir" 2>/dev/null)" ]]; then
        echo "  $util: no files, skipping"
        continue
    fi

    if ! declare -f "apply_$util" >/dev/null 2>&1; then
        echo "  $util: no handler defined, skipping"
        continue
    fi

    "apply_$util"
done
