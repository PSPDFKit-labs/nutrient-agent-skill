#!/bin/bash
# Record demo GIFs using screencapture + real macOS Terminal
# Usage: ./record-gifs.sh [demo|ocr|fill-sign|all]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ASSETS_DIR="$SCRIPT_DIR/assets"
TAPES_DIR="$SCRIPT_DIR/tapes/helpers"
TEMP_DIR="$SCRIPT_DIR/.recording-tmp"

mkdir -p "$ASSETS_DIR" "$TEMP_DIR"

WIN_WIDTH=880
WIN_HEIGHT=520
FPS=6

capture_frames() {
    local win_id="$1"
    local frames_dir="$2"
    local duration="$3"
    local interval
    interval=$(python3 -c "print(1.0/$FPS)")
    local total_frames=$((duration * FPS))
    local frame=0

    while [[ $frame -lt $total_frames ]]; do
        printf "%04d" $frame | xargs -I{} screencapture -l "$win_id" -x "$frames_dir/frame-{}.png" 2>/dev/null &
        sleep "$interval"
        frame=$((frame + 1))
    done
    wait
}

record_gif() {
    local name="$1"
    local script="$2"
    local height="${3:-$WIN_HEIGHT}"
    local duration="${4:-18}"
    local gif="$ASSETS_DIR/${name}.gif"
    local frames_dir="$TEMP_DIR/${name}-frames"

    rm -rf "$frames_dir"
    mkdir -p "$frames_dir"

    echo "🎬 Recording: $name (${duration}s @ ${FPS}fps)"

    # Close stale demo windows
    osascript -e '
        tell application "Terminal"
            repeat with w in windows
                try
                    if (item 1 of bounds of w) is 80 then close w
                end try
            end repeat
        end tell
    ' 2>/dev/null || true
    sleep 0.3

    # Open fresh Terminal with Pro theme
    osascript -e "
        tell application \"Terminal\"
            activate
            do script \"export PS1='> '; clear; sleep 1.5; bash '${script}'\"
            delay 0.5
            set current settings of front window to settings set \"Pro\"
            set bounds of front window to {80, 80, $((80 + WIN_WIDTH)), $((80 + height))}
        end tell
    " 2>/dev/null
    sleep 0.5

    # Get window ID
    local cg_win_id
    cg_win_id=$(osascript -e 'tell application "Terminal" to get id of front window' 2>/dev/null || echo "")
    if [[ -z "$cg_win_id" ]]; then echo "   ❌ No window ID"; return 1; fi
    echo "   Window ID: $cg_win_id"

    # Capture frames
    echo "   ⏺  Capturing..."
    capture_frames "$cg_win_id" "$frames_dir" "$duration"

    local frame_count
    frame_count=$(ls "$frames_dir"/frame-*.png 2>/dev/null | wc -l | tr -d ' ')
    echo "   ✅ $frame_count frames"

    # Convert to GIF (single-pass palette)
    echo "   🔄 Encoding GIF..."
    ffmpeg -y -framerate "$FPS" -i "$frames_dir/frame-%04d.png" \
        -vf "scale=720:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3" \
        -loop 0 \
        "$gif" \
        -loglevel error 2>/dev/null

    echo "   📦 $(du -h "$gif" | cut -f1) → $gif"

    # Close window
    osascript -e '
        tell application "Terminal"
            repeat with w in windows
                try
                    if (item 1 of bounds of w) is 80 then close w
                end try
            end repeat
        end tell
    ' 2>/dev/null || true

    echo ""
}

target="${1:-all}"

case "$target" in
    demo)      record_gif "demo" "$TAPES_DIR/demo-full.sh" 520 16 ;;
    ocr)       record_gif "workflow-ocr" "$TAPES_DIR/ocr-full.sh" 580 20 ;;
    fill-sign) record_gif "workflow-fill-sign" "$TAPES_DIR/fill-sign-full.sh" 600 20 ;;
    all)
        record_gif "demo" "$TAPES_DIR/demo-full.sh" 520 16
        sleep 1
        record_gif "workflow-ocr" "$TAPES_DIR/ocr-full.sh" 580 20
        sleep 1
        record_gif "workflow-fill-sign" "$TAPES_DIR/fill-sign-full.sh" 600 20
        ;;
    *) echo "Usage: $0 [demo|ocr|fill-sign|all]"; exit 1 ;;
esac

echo "🎉 Done!"
ls -lh "$ASSETS_DIR"/*.gif
rm -rf "$TEMP_DIR"
