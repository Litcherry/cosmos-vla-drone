"""Safety checks for baseline drone action plans."""

from __future__ import annotations

from typing import Any


WORKSPACE_BOUNDS = {
    "x": (-3.0, 3.0),
    "y": (-3.0, 3.0),
    "z": (0.0, 3.0),
}


def is_position_in_bounds(position: tuple[float, float, float]) -> bool:
    """Return True if a 3D position is inside the workspace."""

    x, y, z = position
    return (
        WORKSPACE_BOUNDS["x"][0] <= x <= WORKSPACE_BOUNDS["x"][1]
        and WORKSPACE_BOUNDS["y"][0] <= y <= WORKSPACE_BOUNDS["y"][1]
        and WORKSPACE_BOUNDS["z"][0] <= z <= WORKSPACE_BOUNDS["z"][1]
    )


def check_plan_safety(actions: list[dict[str, Any]]) -> list[str]:
    """Return safety violation messages for a validated action list."""

    violations: list[str] = []

    for index, action in enumerate(actions):
        action_name = action["action"]

        if action_name == "move_to":
            position = tuple(action["position"])
            if not is_position_in_bounds(position):
                violations.append(f"action {index} move_to position out of bounds: {position}")

        if action_name == "takeoff":
            altitude = action["altitude"]
            if not WORKSPACE_BOUNDS["z"][0] <= altitude <= WORKSPACE_BOUNDS["z"][1]:
                violations.append(f"action {index} takeoff altitude out of bounds: {altitude}")

        if action_name == "move_above":
            height = action["height"]
            if not WORKSPACE_BOUNDS["z"][0] <= height <= WORKSPACE_BOUNDS["z"][1]:
                violations.append(f"action {index} move_above height out of bounds: {height}")

    return violations


def assert_plan_safe(actions: list[dict[str, Any]]) -> None:
    """Raise ValueError if the plan violates workspace safety constraints."""

    violations = check_plan_safety(actions)
    if violations:
        raise ValueError("; ".join(violations))
