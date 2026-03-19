# Idea: Encode Latent Space Dimensions in Natural Language

Date: 2026-03-19

## The paper
"The latent space of equational theories" (arxiv 2601.20759)
Constructs a 3D embedding via PCA of Stone pairings.

## The idea
If we can describe the PCA dimensions in natural language, we can teach
the model to estimate an equation's position in the latent space:

- Dimension 1: "restrictiveness" — how few magmas satisfy the equation
- Dimension 2: "asymmetry" — whether the equation constrains LHS or RHS more
- Dimension 3: "structural complexity" — depth of nesting

These map to our discovered features:
- satisfaction_score ≈ Dimension 1
- rhs_only_vars ≈ Dimension 2 (partially)
- max_depth ≈ Dimension 3

## Connection to v6's success
v6 already teaches variable analysis (which correlates with Dim 1 and 2).
The 96.7% accuracy suggests these features capture most of the variance.

## What would help beyond v6?
Dim 3 (structural complexity) is NOT well captured by v6.
But adding structural analysis to v6 made it worse (v7, v9).

Perhaps the issue is HOW we describe it, not WHAT we describe.
Evolutionary methods (OpenEvolve) might find better phrasings.

## Status
Speculative. No clear path to improvement beyond v6 through this approach.
Main value: theoretical understanding of why v6 works.
