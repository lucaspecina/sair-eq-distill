# Isomorphisms — Other Fields That Map to Our Problem

Date: 2026-03-18

## Isomorphism 1: DAG Reachability

"Does A imply B?" is exactly "Is B reachable from A in the implication DAG?"

The implication structure forms a partial order:
- 1415 equivalence classes as nodes
- 4824 edges (transitive reduction)
- Height 15, 1 source, 1 sink, diamond shape

This connects to:
- **Graph reachability** — well-studied, compact labeling schemes exist
- **Transitive closure** — chain decomposition, interval labeling
- **Partial order theory** — Dilworth's theorem, chain covers

### Relevant techniques:
- **Interval labeling**: assign each node an interval [a,b]. A is reachable from B
  iff B's interval contains A's label. Works perfectly for trees, extended to DAGs.
- **Chain decomposition**: decompose DAG into chains. Reachability = "there exists
  a chain where A comes before B". Number of chains = width of partial order.
- **Bit vector encoding**: each node gets a bit vector, reachability = bitwise AND.

### Challenge: the model can't compute these algorithms.
We need to translate structural properties into TEXT RULES the model can follow.
The DAG structure tells us WHAT to encode, not HOW to encode it for an LLM.

## Isomorphism 2: Finite Model Theory / Stone Pairings

Paper: "The latent space of equational theories" (arxiv 2601.20759)

Key idea: for each equation, compute the probability that a random finite magma
(size N) satisfies it. This gives a "fingerprint" vector. Equations that imply
each other have nested fingerprints.

Method:
1. Sample 1000 random magmas of size 4-16
2. For each equation, compute P(magma satisfies equation)
3. Apply PCA → 3D embedding
4. In this space, implications form structured chains

### Implication for us:
Could we compute these fingerprints and include them in the cheatsheet?
E.g., "equations with satisfaction probability > 0.5 are weak, < 0.1 are strong"?
The model can't compute the probabilities, but we could precompute and describe
the resulting clusters.

### Possible cheatsheet content:
"Equations that force specific outputs for the operation (like x*y = z*w) have
very low satisfaction probability → they are STRONG and imply most things.
Equations that are easily satisfied by random magmas (like x*(x*x) = x*(x*x))
are WEAK and rarely imply other things."

## Isomorphism 3: Knowledge Distillation / Compression

The competition IS a knowledge distillation problem:
- Teacher: the 22M-cell truth table
- Student: a small LLM reading our cheatsheet
- Objective: maximize the student's accuracy on the teacher's knowledge

This connects to:
- **Rate-distortion theory**: given a bit budget (10KB), what's the max accuracy?
- **Feature selection**: which features of the data are most informative?
- **Lossy compression**: we can't encode all 22M, so what's the best lossy summary?

The optimal cheatsheet encodes the DECISION BOUNDARY, not the data.
I.e., it should describe RULES that separate true from false implications,
not list specific implications.

## Isomorphism 4: Satisfiability / Constraint Propagation

Each equation defines a constraint on the operation table.
"A implies B" means "A's constraints are a superset of B's constraints."

This connects to:
- **SAT solving**: propagation, unit resolution
- **Constraint satisfaction**: arc consistency, backtracking
- **Type systems**: subtyping ("if x has type A, it also has type B")

The subtyping analogy is interesting: implications between equations are like
subtype relationships. Techniques from type inference might help.

## Open questions
- [ ] Can we compute the Stone pairing fingerprints for all 4694 equations?
- [ ] How many chains cover the quotient DAG? (Dilworth's theorem)
- [ ] Can we describe the DAG using interval labels?
- [ ] What's the rate-distortion bound? How close can we get to optimal?
