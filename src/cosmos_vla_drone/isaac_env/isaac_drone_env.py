"""Isaac Sim drone environment placeholder.

This module defines the interface expected from the future Isaac Sim backend.
The real implementation will be enabled on a remote Linux GPU server with
Isaac Sim installed.
"""

from __future__ import annotations

from typing import Any

from cosmos_vla_drone.isaac_env.interfaces import DroneObservation, EnvironmentResult
from cosmos_vla_drone.isaac_env.scene_builder import SceneBuildPlan, SceneBuilder
from cosmos_vla_drone.isaac_env.scene_config import SceneConfig, create_default_scene_config


class IsaacSimUnavailableError(RuntimeError):
    """Raised when Isaac Sim is required but not available."""


class IsaacDroneEnvironment:
    """Placeholder for the future Isaac Sim drone environment."""

    def __init__(
        self,
        scene_config: SceneConfig | None = None,
        scene_builder: SceneBuilder | None = None,
        headless: bool = True,
    ) -> None:
        self.scene_config = scene_config if scene_config is not None else create_default_scene_config()
        self.scene_builder = scene_builder if scene_builder is not None else SceneBuilder()
        self.headless = headless
        self._initialized = False
        self._build_plan: SceneBuildPlan | None = None

    @property
    def build_plan(self) -> SceneBuildPlan | None:
        """Return the latest scene build plan if initialization has been attempted."""

        return self._build_plan

    def create_build_plan(self) -> SceneBuildPlan:
        """Create the scene build plan without launching Isaac Sim."""

        self._build_plan = self.scene_builder.create_build_plan(self.scene_config)
        return self._build_plan

    def initialize(self) -> None:
        """Initialize the Isaac Sim application and scene."""

        self.create_build_plan()
        raise IsaacSimUnavailableError(
            "Isaac Sim is not available in the local development environment. "
            "Run this environment on a remote Linux GPU server with Isaac Sim installed."
        )

    def reset(self) -> DroneObservation:
        """Reset the Isaac Sim scene and return the initial observation."""

        self._require_initialized()
        return DroneObservation(position=self.scene_config.drone.initial_position, airborne=False)

    def execute_plan(self, actions: list[dict[str, Any]]) -> EnvironmentResult:
        """Execute a validated action sequence in Isaac Sim."""

        self._require_initialized()
        raise NotImplementedError("Isaac Sim action execution is not implemented yet.")

    def _require_initialized(self) -> None:
        if not self._initialized:
            raise IsaacSimUnavailableError(
                "IsaacDroneEnvironment.initialize() must succeed before using the environment."
            )