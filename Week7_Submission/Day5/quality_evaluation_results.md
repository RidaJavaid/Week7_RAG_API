# Quality Evaluation Results — Week 7 Day 5

## Evaluation Set

**Source:** `eval_questions.json` — 50 gold questions extracted from Week 6 notebook  
(`Downloads/Week6_Days1_5_FINAL_RAG_Rida_Javaid.ipynb`, cell "Day 3 / Day 5 — 50 gold questions with answers")

**This is the official Week 6 evaluation set.** It covers all 5 source documents:
- `01_machine_learning.txt` (15 questions)
- `02_embeddings.txt` (9 questions)
- `03_rag.txt` (10 questions)
- `04_vector_search.txt` (7 questions)
- `05_chunking_bm25_reranking.txt` (9 questions)

## Quality Metric

**Keyword overlap score** = `|tokens(answer) ∩ tokens(reference)| / |tokens(reference)|`

**Threshold:** 0.40 (40% keyword overlap)

## Normal Mode Results (50 questions, FAST_RERANK=1)

| Metric | Value |
|--------|-------|
| Number of questions | **50** |
| Mean score | **0.6919** |
| Threshold | 0.40 |
| Result | **PASSED** |

Sample high-scoring answers:
- Q1 "What is machine learning?" → exact match, score=1.000
- Q22 "Why is dense retrieval useful for synonyms?" → score=1.000
- Q25 "What is RAG?" → near-perfect match, score=0.938

Sample low-scoring answers:
- Q50 "What is MRR?" → system returns wrong chunk, score=0.000
- Q21 "What is a bi-encoder?" → partial match, score=0.062

## Regression Test (Reranking Disabled)

**Definition:** Set `QUALITY_THRESHOLD = 0.99` in `evaluate_quality.py`.  
With mean score 0.692, the system will fail the threshold → `sys.exit(1)` → CI fails.

Run: `python create_regression_branch.py` (creates test/quality-regression branch)

## GitHub CI Quality Gate

File: `.github/workflows/quality_gate.yml`

- Runs `evaluate_quality.py` on every push
- If mean score < 0.40 → `exit 1` → GitHub Actions step fails (red X)
- Regression branch changes threshold to 0.99 to force failure

## Evidence Files

- `quality_report.json` — full 50-question results JSON (written by evaluator)
- `evaluate_quality.py` — evaluation script
- `eval_questions.json` — 50 gold Q&A pairs (from Week 6 notebook)
- `quality_output.txt` — raw terminal output from evaluation run
