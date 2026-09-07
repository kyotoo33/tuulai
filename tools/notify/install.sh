#!/usr/bin/env bash
# install.sh — install Tuulai's macOS LaunchAgents:
#   com.tuulai.server  — keeps the local app running on 127.0.0.1:8642 (KeepAlive)
#   com.tuulai.notify  — fires the afternoon desktop nudge daily (default 15:00)
#
# This creates persistent per-user background jobs. Run it yourself when you want them on;
# `tools/notify/uninstall.sh` removes them. Notifications only; nothing leaves your machine.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
PY="$REPO/.venv/bin/python"
LA="$HOME/Library/LaunchAgents"
LOGS="$HOME/Library/Logs"     # NOT under ~/Desktop — macOS TCC blocks launchd from writing
                             # a job's stdout/stderr into Desktop/Documents/Downloads (EX_CONFIG/78).
HOUR="${TUULAI_NOTIFY_HOUR:-15}"     # afternoon; override e.g. TUULAI_NOTIFY_HOUR=16
MIN="${TUULAI_NOTIFY_MIN:-0}"

[ -x "$PY" ] || { echo "no venv python at $PY — run 'make' setup first"; exit 1; }
mkdir -p "$LA" "$LOGS"

cat > "$LA/com.tuulai.server.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.tuulai.server</string>
  <key>ProgramArguments</key>
  <array>
    <string>$PY</string><string>-m</string><string>uvicorn</string>
    <string>backend.main:app</string>
    <string>--host</string><string>127.0.0.1</string>
    <string>--port</string><string>8642</string>
  </array>
  <key>WorkingDirectory</key><string>$REPO</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$LOGS/tuulai-server.log</string>
  <key>StandardErrorPath</key><string>$LOGS/tuulai-server.log</string>
</dict></plist>
PLIST

cat > "$LA/com.tuulai.notify.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.tuulai.notify</string>
  <key>ProgramArguments</key>
  <array><string>$PY</string><string>$REPO/tools/notify/notify.py</string></array>
  <key>WorkingDirectory</key><string>$REPO</string>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>$HOUR</integer><key>Minute</key><integer>$MIN</integer></dict>
  <key>StandardOutPath</key><string>$LOGS/tuulai-notify.log</string>
  <key>StandardErrorPath</key><string>$LOGS/tuulai-notify.log</string>
</dict></plist>
PLIST

for label in com.tuulai.server com.tuulai.notify; do
  launchctl unload "$LA/$label.plist" 2>/dev/null || true
  launchctl load "$LA/$label.plist"
done

echo "installed & loaded:"
echo "  com.tuulai.server  → keeps http://127.0.0.1:8642 running"
echo "  com.tuulai.notify  → daily nudge at $(printf '%02d:%02d' "$HOUR" "$MIN")"
echo "remove with: tools/notify/uninstall.sh"
