#!/bin/bash
# Launches an autoresearch session. Restarts if it crashes.
# Reads AUTORESEARCH.md for config (must be ON).
# Usage: bash watch.sh
# To stop: Ctrl+C twice

cd "$(dirname "$0")"

PROMPT="Read AUTORESEARCH.md. If Status is OFF, exit immediately. If ON, read the issues listed in the run config, check their Status headers, and continue from the next step indicated. Work autonomously following the dev-workflow autoresearch protocol. Commit and push frequently."

echo "=== AUTORESEARCH SUPERVISOR ==="
echo "Started at $(date)"
echo "Press Ctrl+C twice to stop"
echo ""

while true; do
    echo "--- Launching session at $(date) ---"
    claude --dangerously-skip-permissions -p "$PROMPT" --max-turns 500
    echo "--- Session exited at $(date). Restarting in 10s... ---"
    sleep 10
done
