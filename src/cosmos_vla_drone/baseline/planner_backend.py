"""Planner backend selection for the baseline VLA drone agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from cosmos_vla_drone.baseline.planner import parse_instruction


PlannerMode = Literal["rule"]


@dataclass(frozen=True)
class PlannerResult:
    """Planner result with source metadata."""

    actions: list[dict[str, Any]]
    source: str
    fallback_reason: str = ""


def plan_instruction(instruction: str, mode: PlannerMode = "rule") -> PlannerResult:
    """Plan an instruction using the requested baseline backend."""

    if mode == "rule":
        return PlannerResult(actions=parse_instruction(instruction), source="rule")

    raise ValueError(f"Unsupported planner mode: {mode}")
