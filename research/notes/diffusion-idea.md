# Diffusion-based cheatsheet optimization — Future research line

Date: 2026-03-19

## Idea
Use diffusion models for discrete text optimization of the cheatsheet.
Instead of evolutionary mutation, use a diffusion process over token space.

## Why it might work
- Diffusion excels at generating structured outputs from noise
- Could explore the token space more smoothly than GA/DE
- Natural way to handle the "discrete optimization" problem

## References to investigate
- Discrete diffusion models for text (D3PM, MDLM)
- Diffusion-based prompt optimization
- Score-based discrete optimization

## Status: PARKED. Focus on evolutionary approach first.
