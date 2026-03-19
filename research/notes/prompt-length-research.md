# Prompt Length Research — Why v6 Works

Date: 2026-03-19

## Literature findings on optimal prompt length

1. **Prompts exceeding 500 words show diminishing returns**
   - Comprehension drops ~12% per 100 words beyond threshold
   - Source: Microsoft/Stanford study

2. **Long prompts increase hallucinations**
   - Hallucinations jump 34% when prompts exceed 2,500 tokens
   - Math accuracy dropped from 92% to 64% with prompt extension (1,800→3,500 tokens)

3. **"Lost in the middle" effect**
   - Models attend best to beginning and end of prompt
   - Information buried in the middle gets ignored

4. **Optimal ranges by task complexity**
   - Simple tasks: 50-100 words
   - Moderate: 150-300 words
   - Complex multi-part: 300-500 words

## Our cheatsheet comparison

| Version | Word count | Tokens (~) | Accuracy |
|---------|-----------|------------|----------|
| v0 | ~250 | ~350 | 72% |
| v1 | ~400 | ~550 | 80% |
| v5 | ~800 | ~1100 | 73% |
| **v6** | **~380** | **~530** | **96.7%** |
| v7 | ~400 | ~560 | 87% |
| v8 | ~320 | ~450 | 80% |

## Analysis

v6 is right in the sweet spot (300-500 words for complex tasks).
v5 crossed the diminishing returns threshold and lost accuracy.
v8 was slightly too terse (missed some helpful context).

The key: v6 has HIGH information density per word. Every sentence
is directly actionable. No filler, no explanations, no examples
that don't add value.

## Implications for optimization

1. Don't add content to v6 unless it PROVABLY helps
2. Any new content must replace existing content, not add to it
3. Focus on making each word count more, not adding more words
4. Structure information with critical content at start and end
5. Future optimization should be surgical edits, not additions
