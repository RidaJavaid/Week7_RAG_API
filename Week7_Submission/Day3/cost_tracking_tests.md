# Cost Tracking Tests — Week 7 Day 3

## Test Suite: `tests/test_cost_tracker.py`

Run:
```bash
python -m pytest tests/test_cost_tracker.py -v
```

## Test Cases

| Test | Verifies |
|------|----------|
| `test_basic_tracking` | Single step timing + report |
| `test_multiple_steps` | Multiple sequential steps |
| `test_cost_accumulation` | `total_cost` = sum of step costs |
| `test_negative_cost_raises` | `ValueError` for cost < 0 |
| `test_cost_budget_exceeded_raises` | `RuntimeError` when budget exceeded |
| `test_get_report_structure` | Report contains all expected fields |
| `test_zero_cost_steps` | Local models have cost 0.0 |
| `test_step_time_recorded_accurately` | `time_seconds` ≥ sleep time |
| `test_total_time_in_report` | Report total_time = sum of steps |

All 9 tests passed.

## Cost Transparency

The cost tracker reports `estimated_cost_usd = 0.0` for all steps in this project
because all models are local. This is not an approximation — there is genuinely
no paid API being called. Infrastructure costs (electricity, hardware) are excluded
per the assignment specification.

## Configuration

File: `cost_tracker.py`

```python
MAX_STEP_SECONDS    = 30.0   # per-step timeout
MAX_REQUEST_SECONDS = 90.0   # total request timeout
MAX_COST_USD        = 0.01   # cost budget (unused for local models)
```

Adjust these constants to enforce different limits.

## Integration

`CostTracker` is used by `rag.ask_rag()` to wrap each stage:
1. Embedding
2. Retrieval
3. Reranking
4. Generation

Each stage is wrapped in a `with tracker.track("StepName"):` block.
Timing and cost are logged automatically.
