"""Task runner that connects baseline planning with a drone environment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cosmos_vla_drone.baseline.runner import BaselineRunResult, run_baseline_task
from cosmos_vla_drone.isaac_env.interfaces import DroneEnvironment, EnvironmentResult


@dataclass(frozen=True)
class TaskRunResult:
    """Full result of planning and executing one task in an environment."""

    instruction: str
    actions: list[dict[str, Any]]
    planner_source: str
    planner_fallback_reason: str
    environment_result: EnvironmentResult

    @property
    def success(self) -> bool:
        return self.environment_result.success

    @property
    def failure_reason(self) -> str:
        return self.environment_result.failure_reason


def run_task_in_environment(
    instruction: str,
    env: DroneEnvironment,
) -> TaskRunResult:
    """Plan a natural language instruction and execute it in an environment."""

    planning_result: BaselineRunResult = run_baseline_task(instruction)
    environment_result = env.execute_plan(planning_result.actions)

    return TaskRunResult(
        instruction=instruction,
        actions=planning_result.actions,
        planner_source=planning_result.planner_source,
        planner_fallback_reason=planning_result.planner_fallback_reason,
        environment_result=environment_result,
    )