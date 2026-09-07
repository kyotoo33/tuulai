#!/usr/bin/env bash
# uninstall.sh — remove Tuulai's LaunchAgents (stops the keep-alive server + daily nudge).
set -euo pipefail
LA="$HOME/Library/LaunchAgents"
for label in com.tuulai.server com.tuulai.notify; do
  launchctl unload "$LA/$label.plist" 2>/dev/null || true
  rm -f "$LA/$label.plist"
  echo "removed $label"
done
echo "Tuulai LaunchAgents uninstalled."
