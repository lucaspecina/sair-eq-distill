# Autoresearch Systems & Techniques — Survey of the Field

**Date:** 2025-03-20
**Purpose:** Identify practical techniques from existing autoresearch systems that we
could adopt to improve our coordinator/worker loop.

---

## 1. Landscape of Autoresearch Systems

The field has exploded since Karpathy's original `autoresearch` repo (a ~630-line
agent that edits `train.py`, runs 5-minute experiments, keeps/reverts by metric).
There are now 30+ public projects. The most relevant to our setup:

| System | Stars | Key Innovation |
|--------|-------|---------------|
| **Karpathy autoresearch** | High | The original: single mutable file, fixed time budget, metric-driven keep/revert |
| **auto-researchtrading** | — | Applied Karpathy pattern to trading. 103 experiments, composite scoring, simplification > addition |
| **AIDE (WecoAI)** | Notable | **Tree search** over solution space instead of linear iteration |
| **AI-Scientist-v2 (Sakana)** | High | **Best-first tree search** with parallel node expansion |
| **AutoResearchClaw** | 7.1k | 23-stage pipeline with **MetaClaw** cross-run learning (lessons → skills) |
| **Sibyl System** | 176 | **Dual-loop**: inner (research) + outer (system self-evolution), 6-agent debate |
| **PBAR** | — | **Population-based** with temperature annealing + git worktree isolation |
| **ARIS** | — | Overnight unattended research with **cross-model adversarial review** |
| **anything-autoresearch** | 1 | Framework for applying autoresearch to ANY domain, 3-layer data isolation |
| **EvoScientist** | ICAIS Best | Six-agent team + RL self-improvement + **EvoMemory** persistent memory |
| **Autogenesis (Skywork)** | — | Self-evolution protocol: Act → Observe → Optimize → Remember |
| **DeepResearch (shtse8)** | 5 | Tree of Thoughts + ReAct methodology for research |
| **NanoResearch** | 124 | 9-stage pipeline, checkpoint-based recovery, multi-model routing |

---

## 2. Deep Dive: Key Systems

### 2.1 Karpathy's autoresearch (the baseline pattern)

What we already use. The core is elegant:
- One mutable file (`train.py` / our `current.txt`)
- Fixed evaluation (immutable `prepare.py` / our `evaluate.py`)
- Fixed time budget (5 min training / our 25 min sessions)
- Binary keep/revert by metric
- Agent reads `program.md` for instructions
- `results.tsv` as experiment log

**What it lacks:** Memory between sessions, exploration strategy, reflection,
population diversity.

### 2.2 auto-researchtrading (Nunchi)

Applied the Karpathy pattern to crypto trading strategies. Key findings after
103 experiments:

- **Composite scoring function** rather than single metric:
  `score = sharpe * sqrt(min(trades/50, 1.0)) - drawdown_penalty - turnover_penalty`
- **Hard cutoffs** that immediately reject bad solutions (score = -999)
- **"The Great Simplification"**: Their biggest gains (+2.0 Sharpe) came from
  REMOVING complexity, not adding it. Systematic ablation was more valuable
  than feature addition.
- **STRATEGIES.md** as narrative memory — rank-ordered discoveries with key
  insight for each, quantified impact.

**Takeaway for us:** We should track which changes REMOVED things and whether
simplification yielded gains. Our `tried_approaches.log` is one-line entries;
a richer narrative with ranked insights would be more useful.

### 2.3 AIDE — Tree Search over Solution Space

This is the biggest architectural difference from our linear approach.

Instead of: try A → evaluate → try B → evaluate → try C → evaluate (linear)

AIDE does: try A → evaluate → branch into A1, A2, A3 → evaluate all → expand
best branch → branch into A2a, A2b → evaluate → ...

**How it works:**
- Each Python script is a NODE in a solution tree
- LLM-generated patches spawn CHILDREN of that node
- Metric feedback PRUNES bad branches and GUIDES the search
- Default: 5 drafts per step (horizontal breadth)
- High-performing branches get preferentially expanded

**Result:** On MLE-Bench (75 Kaggle competitions), tree search wins **4x more
medals** than the best linear agent.

**Why it's better:**
1. Parallel exploration of multiple hypotheses
2. Can backtrack to promising earlier states (not just "current best")
3. Compounding improvements build on proven solutions
4. Dead ends don't block progress — other branches continue

**How we could adopt this:**
- Instead of one `current.txt`, maintain a TREE of cheatsheet variants
- Each worker session could branch from any node, not just current best
- Workers could receive context about the tree structure and pick unexplored branches
- Use git branches or worktrees for isolation (PBAR does this already)

### 2.4 AutoResearchClaw — MetaClaw Cross-Run Learning

The most sophisticated memory system in the field. Key technique: **MetaClaw**.

**How MetaClaw works:**
1. After each run, failures and warnings are captured as "Lessons"
2. Lessons are converted to reusable "Skills" stored in `~/.metaclaw/skills/`
3. Skills are injected into ALL 23 stage prompts via `build_overlay()` in
   subsequent runs
4. 30-day time-decay for skill relevance (recent lessons weigh more)
5. Configurable max skills per run (default: 3) to prevent noise
6. Minimum severity threshold (warnings + errors only)

**Measured impact (A/B tests):**
- Stage retry rate: -24.8%
- Refine cycle count: -40% (2.0 → 1.2 cycles)
- Pipeline completion: +5.3%
- Overall robustness: **+18.3%** composite

**Other techniques:**
- AST-validated code before execution (self-healing)
- PROCEED/REFINE/PIVOT decision gates at analysis stage
- Up to 10 iterations of refinement before forced pivot
- Anti-fabrication guards (citation pruning, disclaimer enforcement)
- Sentinel watchdog for NaN/Inf detection

**How we could adopt this:**
- Convert our `tried_approaches.log` into a structured lessons database
- Extract "skills" from successful approaches and inject them into `program.md`
- Add time-decay so older lessons gradually fade
- Inject the top 3-5 lessons into each worker's prompt dynamically

### 2.5 Sibyl System — Dual-Loop Self-Evolution

**Inner loop (research iteration):**
Literature → Idea Debate (6 agents) → Planning → Pilot Experiments →
Full Experiments → Result Debate (6 agents) → Decision Point

**Outer loop (system evolution):**
After each iteration, the system:
1. Classifies issues into 8 categories
2. Generates improvement plans tied to specific agent roles
3. Records lessons with context (project, iteration, effectiveness metric)
4. Updates its own agent prompts, scheduling strategies, and patterns

**Key technique — Time-Weighted Learning:**
- Lessons include effectiveness tracking with temporal decay
- Recent successes influence prompts more strongly
- Cross-language normalization for issue deduplication
- Agent-routed overlays: lessons inject into SPECIFIC agent prompts, not globally

**Quality Gate Logic:**
Automatic termination when: score >= 8.0 AND iterations >= 2

**How we could adopt this:**
- Add a "meta-loop" that, every N cycles, analyzes what approaches worked/failed
  and updates `program.md` with new guidance
- Route lessons to specific parts of the program (e.g., cheatsheet structure
  lessons vs. evaluation lessons vs. approach selection lessons)
- Add quality gates: if score > X for 3 consecutive cycles, declare victory and
  move to a different optimization dimension

### 2.6 PBAR — Population-Based with Annealing

**How population-based search works here:**
- Multiple branches (cheatsheet variants) evolve in PARALLEL
- Each branch proposes and executes an experiment independently
- Results determine which branches SURVIVE
- Weak branches are ELIMINATED; strong branches are DUPLICATED
- **Temperature-based annealing** controls exploration vs exploitation:
  - High temperature (early) → diverse selection, more exploration
  - Low temperature (late) → concentrate on top performers

**Selection mechanism:** Softmax selection with temperature annealing
(same principle as simulated annealing applied to a population)

**Isolation:** Git worktrees give each branch an independent working directory.
SQLite tracks experiment history persistently.

**How we could adopt this:**
- Run 2-3 workers in parallel, each with a different cheatsheet variant
- Use tournament selection to pick which variants survive
- Anneal selection pressure over time (early: explore diverse formats,
  late: refine the best format)
- Use git worktrees for worker isolation instead of backup/restore dance

### 2.7 ARIS — Cross-Model Adversarial Review

**The key insight:** A single model reviewing its own work creates blind spots.
ARIS uses adversarial cross-model review:

- **Executor:** Claude Code runs experiments, writes code, generates outputs
- **Reviewer:** GPT-5.4 provides rigorous critique from a different perspective
- **Rationale:** "Adversarial bandits are fundamentally harder to game"

**File-based state machine** for memory (no database):
- `CLAUDE.md` — configuration, credentials, hyperparameters
- `NARRATIVE_REPORT.md` — accumulating results, claims, evidence
- Output directories — experiment logs, score histories

**Four composable workflows:**
1. `/idea-discovery` — literature → brainstorm → novelty check → pilot → ranked report
2. `/experiment-bridge` — implement → cross-model code review → deploy → collect results
3. `/auto-review-loop` — 4-round autonomous review with claim validation
4. `/paper-writing` — narrative → outline → figures → LaTeX → auto-improvement

**How we could adopt this:**
- After a worker produces a cheatsheet, use a DIFFERENT model (e.g., gpt-5.4) to
  review it and suggest improvements before evaluation
- Cross-model validation of approach ideas: worker uses one model to generate,
  different model to critique
- 4-round review loops for promising approaches before committing

### 2.8 anything-autoresearch — Three-Layer Data Isolation

**Critical pattern for preventing overfitting:**

1. **Physical Layer:** Test data stored outside agent's working directory
2. **Programmatic Layer:** Environment variable gate controls test set access
3. **Monitoring Layer:** Tracks train-validation gaps with hard discard thresholds

**Multi-agent support:**
- `launch_agents.sh` spawns independent agents with separate worktrees
- `compare_agents.sh` benchmarks results across agents

**Result:** 100% success rate (25/25) vs 15.7% without the autoresearch framework.
This validates that the FRAMEWORK matters as much as the agent.

**How we could adopt this:**
- Separate our eval into "quick dev eval" and "holdout eval" more formally
- Monitor train-dev gap: if score on quick eval >> official eval, we're overfitting
- Auto-discard approaches with large gaps

### 2.9 Autogenesis (Skywork) — Act-Observe-Optimize-Remember

Formal protocol for self-evolving agent systems:

1. **Act:** Agents produce outputs using LLMs and tools
2. **Observe:** Capture outcomes, traces, reasoning, environment feedback
3. **Optimize:** Update prompts/solutions using optimizer (reflection or RL-style)
4. **Remember:** Persist summaries/insights to memory across sessions

**Key architectural feature:** Everything (prompts, agents, tools, environments,
memory) is a "protocol-registered resource" with explicit state, lifecycle, and
versioned interfaces. This makes the system inspectable and debuggable.

**Self Evolution Protocol Layer (SEPL):** Closed-loop operator interface to
propose, assess, and commit improvements with auditable lineage and rollback.

**How we could adopt this:**
- Formalize our improvement loop: every cycle should produce an "observation"
  (structured, not just a note), which feeds into an "optimization" step that
  updates the system itself, not just the cheatsheet.
- Version our `program.md` — track which instructions led to which outcomes.

---

## 3. Technique Comparison Matrix

| Technique | Our Current System | Best Practice (from survey) |
|-----------|-------------------|---------------------------|
| **Search strategy** | Linear (one worker at a time) | Tree search (AIDE) or population-based (PBAR) |
| **Memory between cycles** | `tried_approaches.log` (one-line entries) | Structured lessons → skills injection (MetaClaw), narrative memory (STRATEGIES.md) |
| **Avoiding repeated work** | Manual check of tried_approaches.log | Structured deduplication + cross-language normalization (Sibyl) |
| **Deciding what to try next** | Worker reads context and chooses | Tree search prioritization, debate mechanisms, meta-analysis of past approaches |
| **Evaluation variance** | Accept +-5%, hope for the best | Composite scoring, hard cutoffs, multi-run averaging, train-test gap monitoring |
| **Exploration vs exploitation** | Implicit (worker creativity) | Temperature annealing (PBAR), softmax selection, explicit exploration budget |
| **Reflection** | None | Post-cycle analysis, lesson extraction, system self-update (Sibyl outer loop) |
| **Cross-model validation** | None | Adversarial review with different model (ARIS) |
| **Parallel exploration** | Sequential workers | Multiple workers with worktree isolation (PBAR, anything-autoresearch) |
| **Self-improvement** | Static program.md | MetaClaw skills injection, Sibyl outer loop, Autogenesis SEPL |
| **Failure handling** | Revert and move on | Self-healing code, structured failure analysis, retry with adaptation |
| **Data isolation** | Quick eval vs official eval | Three-layer isolation (physical, programmatic, monitoring) |

---

## 4. Actionable Improvements for Our System

Ranked by expected impact and implementation difficulty.

### Tier 1: High Impact, Low Effort (do these first)

#### 4.1 Structured Lessons Database
**What:** Replace one-line `tried_approaches.log` with a structured file that
captures: approach, score, delta, key insight, failure mode, and reusable lesson.

**Why:** MetaClaw showed -24.8% retry rate and +18.3% robustness from just
injecting past lessons into prompts.

**How:** Create `lessons.jsonl` with entries like:
```json
{
  "cycle": 5,
  "approach": "compress rules with abbreviations",
  "score": 0.76,
  "delta": -0.02,
  "kept": false,
  "failure_mode": "abbreviations confused the model",
  "lesson": "Never use non-standard abbreviations in cheatsheet — models interpret them literally",
  "category": "format",
  "effectiveness": null
}
```
Inject top N lessons (filtered by recency decay) into `program.md` dynamically.

#### 4.2 Ranked Insights Narrative
**What:** Maintain a `STRATEGIES.md` (like auto-researchtrading) with rank-ordered
discoveries, quantified impact, and the key insight for each.

**Why:** Workers currently read `tried_approaches.log` but get no PRIORITIZED
understanding of what matters. A narrative ranking makes the most impactful
findings immediately visible.

**How:** After each KEPT cycle, coordinator updates `STRATEGIES.md` with the
new discovery ranked by score delta. Workers read this alongside tried_approaches.

#### 4.3 Hard Cutoffs for Evaluation
**What:** Add hard cutoffs to evaluation that immediately reject obviously bad
cheatsheets: size > 10KB (already have), score < 0.65 (baseline), TRUE accuracy
< 0.70, FALSE accuracy < 0.60.

**Why:** auto-researchtrading uses hard cutoffs (-999 score) to prevent wasting
evaluation budget on clearly broken solutions.

**How:** Add cutoff checks in coordinator's Step 4, before the full 200-problem eval.

#### 4.4 Cross-Model Review Step
**What:** After worker produces a cheatsheet, before official eval, have a
different model (gpt-5.4) review it for obvious issues.

**Why:** ARIS demonstrates that cross-model adversarial review catches blind
spots a single model misses. Cheap insurance.

**How:** Add a step between worker completion and eval: call gpt-5.4 with the
cheatsheet and ask "review this for: redundancy, contradictions, wasted bytes,
missing important rules". Feed suggestions to next worker.

### Tier 2: High Impact, Medium Effort

#### 4.5 Tree Search Instead of Linear
**What:** Maintain a tree of cheatsheet variants instead of a single `current.txt`.
Workers can branch from any node, not just the current best.

**Why:** AIDE's tree search wins 4x more medals than linear on MLE-Bench.
Our linear approach means a good change that slightly hurts the current score
gets permanently lost, even if it would enable future improvements.

**How:**
- Store variants in `cheatsheets/tree/` with parent links
- Track a tree in `cheatsheet_tree.json`: `{id, parent_id, score, approach, path}`
- Workers receive the tree structure and can choose to branch from any promising
  node, not just the highest scorer
- Selection: best-first (expand highest-scoring unexplored node) or UCB
  (balance exploration of under-explored branches)

#### 4.6 Population-Based Parallel Workers
**What:** Run 2-3 workers simultaneously, each starting from a different
cheatsheet variant.

**Why:** PBAR demonstrates population-based approaches explore the space more
efficiently. We're sequentially exploring one path at a time.

**How:**
- Use git worktrees (one per worker) for isolation
- Each worker gets a different starting cheatsheet
- After all workers finish, evaluate all variants
- Tournament selection: keep the best, discard the rest
- Optionally: temperature annealing on selection (early cycles: more random
  selection; later: increasingly greedy)

#### 4.7 Meta-Loop for System Self-Improvement
**What:** Every 5-10 cycles, run a "meta-analysis" step that reviews all
cycle results and updates `program.md` with new guidance.

**Why:** Sibyl's outer loop and MetaClaw both show that evolving the SYSTEM
(not just the artifact) yields compounding improvements. Our `program.md` is
static — it never learns from our experiments.

**How:**
- Coordinator periodically (every N cycles) spawns a meta-worker
- Meta-worker reads all cycle notes, tried_approaches.log, results.tsv
- Produces: updated guidance for workers, new anti-patterns to avoid,
  promising directions to double down on
- Coordinator patches `program.md` with meta-worker's recommendations
- Track program.md versions to see which instructions correlate with
  better outcomes

#### 4.8 Evaluation Variance Reduction
**What:** Run evaluation 2-3 times and take the median/mean, not a single noisy
measurement.

**Why:** Our eval has +-5% variance. A 3% improvement could be noise.
No system we surveyed explicitly addresses this well, but composite scoring
and multi-run evaluation are standard in ML.

**How:**
- For keep/revert decisions, run 2 evals (400 problems total) and average
- Only keep if mean score > best + 1% (to account for remaining noise)
- Track variance per approach (some approaches may be high-variance)

### Tier 3: High Impact, High Effort (invest when ready)

#### 4.9 Full Tree Search with UCB Selection
**What:** Implement proper Upper Confidence Bound (UCB) for node selection in
the cheatsheet tree.

**Why:** UCB balances exploration (trying under-explored branches) with
exploitation (expanding high-scoring branches). This is the gold standard
for exploration/exploitation tradeoffs.

**How:** UCB score = mean_score + C * sqrt(ln(total_visits) / node_visits).
Workers are sent to branches with highest UCB score. C controls exploration
pressure (anneal it over time like PBAR's temperature).

#### 4.10 Skill Extraction and Injection Pipeline
**What:** Automatically extract reusable "skills" from successful cycles and
inject them into worker prompts.

**Why:** MetaClaw's lesson-to-skill pipeline is the most impactful single
technique in the survey (+18.3% robustness).

**How:**
- After KEPT cycles, extract the core technique as a structured skill
- Store in `skills.jsonl` with: description, trigger condition, effectiveness
- Before spawning workers, select top-3 relevant skills (by recency + effectiveness)
- Inject into the worker's prompt as "proven techniques" section
- Track skill effectiveness: does the worker using skill X produce better results?
- Decay skills that stop being effective

#### 4.11 Approach Generation via Debate
**What:** Instead of having workers choose their own approach, use multi-agent
debate to generate and rank approach candidates.

**Why:** Sibyl uses 6-agent debate for hypothesis generation, producing more
diverse and higher-quality ideas than single-agent reasoning.

**How:**
- Before each cycle, spawn a brief "strategist" session
- Multiple agents (or multiple calls to the same model with different personas)
  propose approaches
- Rank by novelty (vs tried_approaches) and expected impact
- Feed the top-ranked approach to the worker as a specific assignment

---

## 5. Key Findings and Principles

### What makes autoresearch loops effective (from the survey):

1. **Constraint is key.** Every successful system constrains what the agent can
   modify (single mutable file) and what it cannot (immutable eval, fixed budget).
   Our setup does this well.

2. **Memory compounds.** Systems with structured cross-run memory (MetaClaw,
   Sibyl, EvoMemory) dramatically outperform memoryless loops. Our memory
   (`tried_approaches.log`) is the weakest link.

3. **Tree search beats linear search.** AIDE's 4x improvement over linear agents
   is the strongest quantitative finding. Maintaining a tree of solutions instead
   of a single current-best is the highest-leverage architectural change.

4. **Simplification often beats addition.** auto-researchtrading's biggest gains
   came from removing features. We should explicitly try ablation studies on our
   cheatsheet (remove sections, see if score improves).

5. **Cross-model review catches blind spots.** ARIS's adversarial review is cheap
   insurance. Having a different model critique work before evaluation prevents
   systematic blind spots.

6. **The framework matters as much as the agent.** anything-autoresearch went from
   15.7% to 100% success rate just by providing the right structure. Our
   `program.md` is already good; making it adaptive would be even better.

7. **Population diversity prevents local optima.** Running multiple parallel
   paths (PBAR, git worktrees) explores more of the solution space than
   sequential single-path search.

8. **Evaluation noise is the silent killer.** Our +-5% variance means we might
   be rejecting improvements and keeping regressions. Multi-run averaging and
   composite scoring address this.

---

## 6. Recommended Implementation Order

**Phase 1 (immediate, 1-2 sessions):**
- [ ] Structured lessons database (4.1)
- [ ] Hard cutoffs for evaluation (4.3)
- [ ] Ranked insights narrative (4.2)

**Phase 2 (next week):**
- [ ] Cross-model review step (4.4)
- [ ] Evaluation variance reduction (4.8)
- [ ] Meta-loop for system self-improvement (4.7)

**Phase 3 (when current approach plateaus):**
- [ ] Tree search instead of linear (4.5)
- [ ] Population-based parallel workers (4.6)
- [ ] Full UCB selection (4.9)
- [ ] Skill extraction and injection (4.10)
- [ ] Debate-based approach generation (4.11)

---

## 7. Sources

- Karpathy autoresearch: https://github.com/karpathy/autoresearch
- auto-researchtrading: https://github.com/Nunchi-trade/auto-researchtrading
- AIDE: https://github.com/WecoAI/aideml
- AI-Scientist-v2: https://github.com/SakanaAI/AI-Scientist-v2
- AutoResearchClaw + MetaClaw: https://github.com/aiming-lab/AutoResearchClaw
- Sibyl System: https://github.com/Sibyl-Research-Team/AutoResearch-SibylSystem
- PBAR: https://github.com/garrettekinsman/pbar
- ARIS: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep
- anything-autoresearch: https://github.com/jialinyi94/anything-autoresearch
- EvoScientist: https://github.com/EvoScientist/EvoScientist
- Autogenesis: https://github.com/SkyworkAI/DeepResearchAgent
- NanoResearch: https://github.com/OpenRaiser/NanoResearch
- Awesome-Auto-Research: https://github.com/EdwardLeeLPZ/Awesome-Auto-Research
- FML-bench: https://github.com/qrzou/FML-bench
