#!/bin/bash
# Watcher for autoresearch overnight runs.
# Restarts Claude Code if it exits for any reason.
# Usage: bash watch.sh
#
# To stop: Ctrl+C twice, or kill the terminal.

cd "$(dirname "$0")"

PROMPT="Read program.md and continue the autoresearch experiment loop. Check results.tsv and git log to see what has been done. Then continue from where we left off."

echo "=== eq-distill autoresearch watcher ==="
echo "Starting at $(date)"
echo "Press Ctrl+C twice to stop"
echo ""

ITERATION=0
while true; do
    ITERATION=$((ITERATION + 1))
    echo "--- Watcher iteration $ITERATION at $(date) ---"

    claude --dangerously-skip-permissions -p "$PROMPT" --max-turns 200

    EXIT_CODE=$?
    echo ""
    echo "--- Claude exited with code $EXIT_CODE at $(date) ---"
    echo "Restarting in 10 seconds..."
    sleep 10
done
