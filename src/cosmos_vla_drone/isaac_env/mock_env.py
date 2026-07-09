"""Lightweight mock environment used before Isaac Sim integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from cosmos_vla_drone.baseline.safety import assert_plan_safe
from cosmos_vla_drone.isaac_env.interfaces import (
    DroneObservation,
    EnvironmentEvent,
    EnvironmentResult,
)


DEFAULT_TARGETS = {
    "red": np.array([1.5, 0.8, 0.0], dtype=float),
    "blue": np.array([-1.4, 1.0, 0.0], dtype=float),
    "green": np.array([0.4, -1.6, 0.0], dtype=float),
}


def _position_tuple(position: np.ndarray) -> tuple[float, float, float]:
    """Convert a numpy position vector to a fixed-size 3D tuple."""

    return (float(position[0]), float(position[1]), float(position[2]))


@dataclass
class MockDroneState:
    """Simple drone state for baseline execution."""

    position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0], dtype=float))
    airborne: bool = False
    last_target: str | None = None


class MockDroneEnvironment:
    """A deterministic mock drone environment with colored targets."""

    def __init__(self, targets: dict[str, np.ndarray] | None = None) -> None:
        self.targets = targets if targets is not None else DEFAULT_TARGETS
        self.state = MockDroneState()

    def reset(self) -> DroneObservation:
        """Reset the drone to its initial state."""

        self.state = MockDroneState()
        return self._observation()

    def execute_plan(self, actions: list[dict[str, Any]]) -> EnvironmentResult:
        """Execute a validated action sequence."""

        try:
            assert_plan_safe(actions)
            events: list[EnvironmentEvent] = []

            for action in actions:
                event = self._execute_action(action)
                events.append(event)

            return EnvironmentResult(
                success=True,
                final_observation=self._observation(),
                events=events,
            )
        except Exception as exc:
            return EnvironmentResult(
                success=False,
                final_observation=self._observation(),
                events=[],
                failure_reason=type(exc).__name__ + ":" + str(exc),
            )

    def _execute_action(self, action: dict[str, Any]) -> EnvironmentEvent:
        action_name = action["action"]

        if action_name == "takeoff":
            self.state.position[2] = float(action["altitude"])
            self.state.airborne = True

        elif action_name == "search":
            target = action["target"]
            if target not in self.targets:
                raise ValueError(f"target not found: {target}")
            self.state.last_target = target

        elif action_name == "move_to":
            self.state.position = np.array(action["position"], dtype=float)

        elif action_name == "move_above":
            target = action["target"]
            if target not in self.targets:
                raise ValueError(f"target not found: {target}")
            target_position = self.targets[target]
            self.state.position = np.array(
                [target_position[0], target_position[1], float(action["height"])],
                dtype=float,
            )
            self.state.last_target = target

        elif action_name == "hover":
            pass

        elif action_name == "land":
            self.state.position[2] = 0.0
            self.state.airborne = False

        else:
            raise ValueError(f"unsupported action: {action_name}")

        return EnvironmentEvent(
            action=action_name,
            position=_position_tuple(self.state.position),
            airborne=self.state.airborne,
            last_target=self.state.last_target,
        )

    def _observation(self) -> DroneObservation:
        return DroneObservation(
            position=_position_tuple(self.state.position),
            airborne=self.state.airborne,
            last_target=self.state.last_target,
        )