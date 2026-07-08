"""Action schema for the baseline VLA drone agent."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError, model_validator


ActionName = Literal["takeoff", "search", "move_to", "move_above", "hover", "land"]
TargetColor = Literal["red", "blue", "green"]


class Action(BaseModel):
    """A single validated drone action."""

    action: ActionName
    altitude: float | None = Field(default=None, ge=0.2, le=3.0)
    target: TargetColor | None = None
    position: tuple[float, float, float] | None = None
    height: float | None = Field(default=None, ge=0.2, le=2.5)
    duration: float | None = Field(default=None, ge=0.5, le=30.0)

    @model_validator(mode="after")
    def validate_required_fields(self) -> "Action":
        if self.action == "takeoff" and self.altitude is None:
            raise ValueError("takeoff requires altitude")

        if self.action == "search" and self.target is None:
            raise ValueError("search requires target")

        if self.action == "move_to" and self.position is None:
            raise ValueError("move_to requires position")

        if self.action == "move_above":
            if self.target is None:
                raise ValueError("move_above requires target")
            if self.height is None:
                raise ValueError("move_above requires height")

        if self.action == "hover" and self.duration is None:
            raise ValueError("hover requires duration")

        return self


class Plan(BaseModel):
    """A validated sequence of drone actions."""

    actions: list[Action] = Field(min_length=1)


def validate_plan(raw_actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate raw planner output and return normalized action dictionaries."""

    try:
        plan = Plan(actions=[Action(**item) for item in raw_actions])
    except ValidationError as exc:
        raise ValueError(f"Invalid action plan: {exc}") from exc

    return [action.model_dump(exclude_none=True) for action in plan.actions]
