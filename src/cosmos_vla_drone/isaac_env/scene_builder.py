"""Scene builder abstraction for future Isaac Sim integration."""

from __future__ import annotations

from dataclasses import dataclass

from cosmos_vla_drone.isaac_env.scene_config import SceneConfig


@dataclass(frozen=True)
class SceneBuildStep:
    """One planned scene construction step."""

    kind: str
    name: str
    details: dict[str, object]


@dataclass(frozen=True)
class SceneBuildPlan:
    """A backend-independent description of how a scene should be built."""

    scene_name: str
    steps: tuple[SceneBuildStep, ...]


class SceneBuilder:
    """Build a backend-independent scene plan from a SceneConfig."""

    def create_build_plan(self, config: SceneConfig) -> SceneBuildPlan:
        """Create a serializable plan for constructing the scene."""

        steps: list[SceneBuildStep] = [
            SceneBuildStep(
                kind="ground_plane",
                name="ground_plane",
                details={"position": (0.0, 0.0, 0.0)},
            ),
            SceneBuildStep(
                kind="drone",
                name=config.drone.name,
                details={
                    "initial_position": config.drone.initial_position,
                    "max_speed": config.drone.max_speed,
                    "max_acceleration": config.drone.max_acceleration,
                },
            ),
        ]

        for target in config.targets:
            steps.append(
                SceneBuildStep(
                    kind="target",
                    name=target.name,
                    details={
                        "color": target.color,
                        "position": target.position,
                    },
                )
            )

        for wall in config.walls:
            steps.append(
                SceneBuildStep(
                    kind="wall",
                    name=wall.name,
                    details={
                        "position": wall.position,
                        "size": wall.size,
                    },
                )
            )

        for camera in config.cameras:
            steps.append(
                SceneBuildStep(
                    kind="camera",
                    name=camera.name,
                    details={
                        "resolution": camera.resolution,
                        "fov_degrees": camera.fov_degrees,
                        "enable_depth": camera.enable_depth,
                    },
                )
            )

        return SceneBuildPlan(scene_name=config.name, steps=tuple(steps))