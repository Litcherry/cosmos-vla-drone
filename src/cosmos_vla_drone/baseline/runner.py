"""Baseline runner for planning natural language drone tasks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from cosmos_vla_drone.baseline.planner_backend import PlannerMode, plan_instruction


@dataclass(frozen=True)
class BaselineRunResult:
    """Structured result for a baseline planning run."""

    instruction: str
    actions: list[dict[str, Any]]
    planner_source: str
    planner_fallback_reason: str = ""


def run_baseline_task(instruction: str, planner: PlannerMode = "rule") -> BaselineRunResult:
    """Run the baseline planner pipeline for one natural language instruction."""

    planner_result = plan_instruction(instruction, mode=planner)
    return BaselineRunResult(
        instruction=instruction,
        actions=planner_result.actions,
        planner_source=planner_result.source,
        planner_fallback_reason=planner_result.fallback_reason,
    )


def run_baseline_task_as_dict(instruction: str, planner: PlannerMode = "rule") -> dict[str, Any]:
    """Run a baseline task and return a JSON-serializable dictionary."""

    return asdict(run_baseline_task(instruction=instruction, planner=planner))