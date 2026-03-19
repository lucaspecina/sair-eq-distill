#!/bin/bash
# Watcher for autoresearch overnight runs.
# Restarts Claude Code if it exits for any reason.
# Usage: bash watch.sh
#
# To stop: Ctrl+C twice, or kill the terminal.

cd "$(dirname "$0")"

# Activate conda environment
eval "$(conda shell.bash hook)"
conda activate eq-distill

PROMPT="Read CLAUDE.md (start there section), then TODO.md to see pending tasks. Work on the highest priority pending task. Document findings in research/notes/. Commit progress. Move to the next task. NEVER STOP. The human is asleep."

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
