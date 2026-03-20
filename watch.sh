#!/bin/bash
# Autoresearch supervisor for cheatsheet optimization.
# Runs 30-minute cycles: spawn agent → warn → collect summary → evaluate → keep/revert → repeat
#
# Usage: bash watch.sh
# To stop: Ctrl+C twice, or kill the terminal.

cd "$(dirname "$0")"

PYTHON="/c/Users/YT40432/miniconda3/envs/eq-distill/python.exe"
SESSION_MINUTES=25
WARN_MINUTES=20
EVAL_MODEL="gpt-5-nano"
EVAL_SAMPLE=200
BEST_CHEATSHEET="cheatsheets/best.txt"
CURRENT_CHEATSHEET="cheatsheets/current.txt"
RESULTS_FILE="results.tsv"
TRIED_LOG="tried_approaches.log"

PROMPT="Read program.md FIRST. Follow it exactly. You have ${SESSION_MINUTES} minutes. GO."

echo "=== AUTORESEARCH SUPERVISOR ==="
echo "Started at $(date)"
echo "Session budget: ${SESSION_MINUTES} min"
echo "Eval: ${EVAL_MODEL}, ${EVAL_SAMPLE} problems"
echo "Press Ctrl+C twice to stop"
echo ""

# Ensure best.txt exists
if [ ! -f "$BEST_CHEATSHEET" ]; then
    cp "$CURRENT_CHEATSHEET" "$BEST_CHEATSHEET"
fi

# Ensure results.tsv exists
if [ ! -f "$RESULTS_FILE" ]; then
    echo -e "timestamp\tscore\tapproach\tstatus" > "$RESULTS_FILE"
fi

# Get current best score
get_score() {
    local cs="$1"
    $PYTHON -u eval/evaluate.py --cheatsheet "$cs" --models "$EVAL_MODEL" --sample "$EVAL_SAMPLE" --concurrent 20 2>&1 | grep "^RESULT:" | grep -oP 'accuracy=\K[0-9.]+'
}

ITERATION=0
while true; do
    ITERATION=$((ITERATION + 1))
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M")
    echo ""
    echo "============================================================"
    echo "CYCLE $ITERATION | $TIMESTAMP"
    echo "============================================================"

    # --- Phase 1: Launch agent ---
    echo "[${TIMESTAMP}] Launching agent session..."

    # Start claude in background
    claude --dangerously-skip-permissions -p "$PROMPT" --max-turns 200 &
    CLAUDE_PID=$!

    # --- Phase 2: Wait, then warn ---
    echo "[${TIMESTAMP}] Agent running (PID: $CLAUDE_PID)..."
    sleep $((WARN_MINUTES * 60))

    # Send 5-minute warning
    echo "[$(date +%H:%M)] Sending 5-minute warning..."
    # Note: can't send messages to running claude easily.
    # The agent should self-manage time based on program.md instructions.

    # Wait remaining time
    sleep $(( (SESSION_MINUTES - WARN_MINUTES) * 60 ))

    # --- Phase 3: Kill agent ---
    echo "[$(date +%H:%M)] Session time up. Stopping agent..."
    kill $CLAUDE_PID 2>/dev/null
    wait $CLAUDE_PID 2>/dev/null
    sleep 5

    # --- Phase 4: Evaluate ---
    echo "[$(date +%H:%M)] Evaluating cheatsheet..."

    # Check size
    SIZE=$(wc -c < "$CURRENT_CHEATSHEET")
    if [ "$SIZE" -gt 10240 ]; then
        echo "  ERROR: Cheatsheet is $SIZE bytes (limit 10240). Reverting."
        cp "$BEST_CHEATSHEET" "$CURRENT_CHEATSHEET"
        echo -e "${TIMESTAMP}\t0\tsize_violation\tREVERTED" >> "$RESULTS_FILE"
        continue
    fi

    # Run evaluation
    NEW_SCORE=$(get_score "$CURRENT_CHEATSHEET")
    BEST_SCORE=$(get_score "$BEST_CHEATSHEET")

    echo "  New score:  ${NEW_SCORE:-FAILED}"
    echo "  Best score: ${BEST_SCORE:-UNKNOWN}"

    # --- Phase 5: Keep or Revert ---
    if [ -n "$NEW_SCORE" ] && [ -n "$BEST_SCORE" ]; then
        # Compare (using python for float comparison)
        IMPROVED=$($PYTHON -c "print('yes' if float('${NEW_SCORE}') > float('${BEST_SCORE}') else 'no')")

        if [ "$IMPROVED" = "yes" ]; then
            echo "  *** IMPROVED! Keeping new cheatsheet. ***"
            cp "$CURRENT_CHEATSHEET" "$BEST_CHEATSHEET"
            git add "$CURRENT_CHEATSHEET" "$BEST_CHEATSHEET"
            git commit -m "autoresearch: improved to ${NEW_SCORE} (cycle $ITERATION)"
            echo -e "${TIMESTAMP}\t${NEW_SCORE}\tcycle_${ITERATION}\tKEPT" >> "$RESULTS_FILE"
        else
            echo "  No improvement. Reverting cheatsheet."
            cp "$BEST_CHEATSHEET" "$CURRENT_CHEATSHEET"
            echo -e "${TIMESTAMP}\t${NEW_SCORE}\tcycle_${ITERATION}\tREVERTED" >> "$RESULTS_FILE"
        fi
    else
        echo "  Evaluation failed. Reverting."
        cp "$BEST_CHEATSHEET" "$CURRENT_CHEATSHEET"
        echo -e "${TIMESTAMP}\t0\tcycle_${ITERATION}_eval_fail\tREVERTED" >> "$RESULTS_FILE"
    fi

    echo "[$(date +%H:%M)] Cycle $ITERATION complete. Restarting in 30 seconds..."
    sleep 30
done
