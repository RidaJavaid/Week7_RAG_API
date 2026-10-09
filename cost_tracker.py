
import logging
import time
from contextlib import contextmanager

# -----------------------------------
# Configuration
# -----------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

MAX_STEP_SECONDS = 30.0
MAX_REQUEST_SECONDS = 90.0
MAX_COST_USD = 0.01


# -----------------------------------
# Cost and Time Tracker
# -----------------------------------

class CostTracker:

    def __init__(self):
        self.total_cost = 0.0
        self.steps = []
        self.request_start = time.perf_counter()

    @contextmanager
    def track(self, step_name, estimated_cost=0.0):

        # Validate estimated cost
        if estimated_cost < 0:
            raise ValueError(
                "Estimated cost cannot be negative"
            )

        # Check cost budget
        if self.total_cost + estimated_cost > MAX_COST_USD:
            raise RuntimeError(
                "Cost budget exceeded"
            )

        start = time.perf_counter()

        try:
            yield

        finally:
            elapsed = time.perf_counter() - start

            self.total_cost += estimated_cost

            # Store step information
            step = {
                "step": step_name,
                "time_seconds": round(elapsed, 4),
                "estimated_cost_usd": estimated_cost
            }

            self.steps.append(step)

            # Log step performance
            logger.info(
                "%s | Time: %.4fs | Cost: $%.6f",
                step_name,
                elapsed,
                estimated_cost
            )

            # Check step time limit
            if elapsed > MAX_STEP_SECONDS:
                raise TimeoutError(
                    f"{step_name} exceeded "
                    f"{MAX_STEP_SECONDS} seconds"
                )

            # Check total request time
            total_elapsed = (
                time.perf_counter()
                - self.request_start
            )

            if total_elapsed > MAX_REQUEST_SECONDS:
                raise TimeoutError(
                    "Total request time limit exceeded"
                )

    def get_report(self):
        """Return complete tracking report."""

        total_time = sum(
            step["time_seconds"]
            for step in self.steps
        )

        return {
            "steps": self.steps,
            "total_time_seconds": round(total_time, 4),
            "estimated_api_cost_usd": round(
                self.total_cost, 6
            ),
            "max_step_seconds": MAX_STEP_SECONDS,
            "max_request_seconds": MAX_REQUEST_SECONDS,
            "max_cost_usd": MAX_COST_USD
        }
