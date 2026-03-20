#!/bin/bash
# Launches the coordinator session. Restarts if it crashes.
# Usage: bash watch.sh
# To stop: Ctrl+C twice

cd "$(dirname "$0")"

PROMPT="Read coordinator.md. Follow it exactly. Execute the loop FOREVER. Start now."

echo "=== AUTORESEARCH SUPERVISOR ==="
echo "Started at $(date)"
echo "Press Ctrl+C twice to stop"
echo ""

while true; do
    echo "--- Launching coordinator at $(date) ---"
    claude --dangerously-skip-permissions -p "$PROMPT" --max-turns 500
    echo "--- Coordinator exited at $(date). Restarting in 10s... ---"
    sleep 10
done
