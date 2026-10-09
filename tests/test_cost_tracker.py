"""
Week 7 Day 3 — CostTracker unit tests.
Run with:  pytest tests/test_cost_tracker.py -v
"""

import time
import pytest
from cost_tracker import CostTracker, MAX_STEP_SECONDS, MAX_REQUEST_SECONDS, MAX_COST_USD


def test_basic_tracking():
    tracker = CostTracker()
    with tracker.track("TestStep"):
        time.sleep(0.01)
    assert len(tracker.steps) == 1
    step = tracker.steps[0]
    assert step["step"] == "TestStep"
    assert step["time_seconds"] >= 0.01
    assert step["estimated_cost_usd"] == 0.0


def test_multiple_steps():
    tracker = CostTracker()
    with tracker.track("Step1"):
        time.sleep(0.005)
    with tracker.track("Step2"):
        time.sleep(0.005)
    assert len(tracker.steps) == 2
    assert tracker.steps[0]["step"] == "Step1"
    assert tracker.steps[1]["step"] == "Step2"


def test_cost_accumulation():
    tracker = CostTracker()
    with tracker.track("Embedding", estimated_cost=0.001):
        pass
    with tracker.track("Retrieval", estimated_cost=0.002):
        pass
    assert round(tracker.total_cost, 4) == 0.003


def test_negative_cost_raises():
    tracker = CostTracker()
    with pytest.raises(ValueError, match="negative"):
        with tracker.track("Bad", estimated_cost=-0.001):
            pass


def test_cost_budget_exceeded_raises():
    tracker = CostTracker()
    tracker.total_cost = MAX_COST_USD  # max out the budget
    with pytest.raises(RuntimeError, match="Cost budget exceeded"):
        with tracker.track("Overflow", estimated_cost=0.001):
            pass


def test_get_report_structure():
    tracker = CostTracker()
    with tracker.track("Embedding"):
        time.sleep(0.005)
    report = tracker.get_report()
    assert "steps" in report
    assert "total_time_seconds" in report
    assert "estimated_api_cost_usd" in report
    assert "max_step_seconds" in report
    assert "max_request_seconds" in report
    assert "max_cost_usd" in report
    assert report["max_step_seconds"] == MAX_STEP_SECONDS
    assert report["max_request_seconds"] == MAX_REQUEST_SECONDS
    assert report["max_cost_usd"] == MAX_COST_USD


def test_zero_cost_steps():
    tracker = CostTracker()
    for name in ["Embedding", "Retrieval", "Reranking", "Generation"]:
        with tracker.track(name, estimated_cost=0.0):
            pass
    assert tracker.total_cost == 0.0
    assert len(tracker.steps) == 4


def test_step_time_recorded_accurately():
    tracker = CostTracker()
    with tracker.track("Timed"):
        time.sleep(0.05)
    assert tracker.steps[0]["time_seconds"] >= 0.05
    assert tracker.steps[0]["time_seconds"] < 1.0  # sanity upper bound


def test_total_time_in_report():
    tracker = CostTracker()
    with tracker.track("A"):
        time.sleep(0.01)
    with tracker.track("B"):
        time.sleep(0.01)
    report = tracker.get_report()
    assert report["total_time_seconds"] >= 0.02
