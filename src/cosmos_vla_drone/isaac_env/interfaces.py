"""Shared environment interfaces for mock and Isaac Sim drone environments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

Vector3 = tuple[float, float, float]


@dataclass(frozen=True)
class DroneObservation:
    """Observation returned by a drone environment."""

    position: Vector3
    airborne: bool
    last_target: str | None = None
    rgb_frame_path: str | None = None
    depth_frame_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EnvironmentEvent:
    """One event generated while executing an action."""

    action: str
    position: Vector3
    airborne: bool
    last_target: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EnvironmentResult:
    """Result of executing an action plan in an environment."""

    success: bool
    final_observation: DroneObservation
    events: list[EnvironmentEvent]
    failure_reason: str = ""

@runtime_checkable
class DroneEnvironment(Protocol):
    """Common interface for mock and Isaac Sim drone environments."""

    def reset(self) -> DroneObservation:
        """Reset the environment and return the initial observation."""
        ...

    def execute_plan(self, actions: list[dict[str, Any]]) -> EnvironmentResult:
        """Execute a validated action sequence and return the result."""
        ...