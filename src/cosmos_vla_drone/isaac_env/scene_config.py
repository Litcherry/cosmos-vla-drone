"""Scene configuration for mock and Isaac Sim drone environments."""

from __future__ import annotations

from dataclasses import dataclass, field

from cosmos_vla_drone.isaac_env.interfaces import Vector3


@dataclass(frozen=True)
class TargetConfig:
    """Configuration for a target object in the scene."""

    name: str
    color: str
    position: Vector3


@dataclass(frozen=True)
class WallConfig:
    """Configuration for a wall obstacle in the scene."""

    name: str
    position: Vector3
    size: Vector3


@dataclass(frozen=True)
class CameraConfig:
    """Configuration for a drone-mounted camera."""

    name: str
    resolution: tuple[int, int] = (640, 480)
    fov_degrees: float = 90.0
    enable_depth: bool = True


@dataclass(frozen=True)
class DroneConfig:
    """Configuration for the simulated drone."""

    name: str = "drone"
    initial_position: Vector3 = (0.0, 0.0, 0.0)
    max_speed: float = 1.0
    max_acceleration: float = 0.5


@dataclass(frozen=True)
class SceneConfig:
    """Complete scene configuration."""

    name: str
    drone: DroneConfig = field(default_factory=DroneConfig)
    targets: tuple[TargetConfig, ...] = field(default_factory=tuple)
    walls: tuple[WallConfig, ...] = field(default_factory=tuple)
    cameras: tuple[CameraConfig, ...] = field(default_factory=tuple)


def create_default_scene_config() -> SceneConfig:
    """Create the default colored-target drone scene."""

    return SceneConfig(
        name="default_colored_target_scene",
        targets=(
            TargetConfig(name="red_target", color="red", position=(1.5, 0.8, 0.0)),
            TargetConfig(name="blue_target", color="blue", position=(-1.4, 1.0, 0.0)),
            TargetConfig(name="green_target", color="green", position=(0.4, -1.6, 0.0)),
        ),
        cameras=(
            CameraConfig(name="front_rgbd_camera"),
        ),
    )


def create_maze_scene_config() -> SceneConfig:
    """Create a simple maze-like scene for future exploration experiments."""

    return SceneConfig(
        name="simple_maze_scene",
        targets=(
            TargetConfig(name="red_target", color="red", position=(2.0, 1.5, 0.0)),
            TargetConfig(name="blue_target", color="blue", position=(-2.0, 1.5, 0.0)),
            TargetConfig(name="green_target", color="green", position=(0.0, -2.0, 0.0)),
        ),
        walls=(
            WallConfig(name="wall_left", position=(-1.0, 0.0, 0.75), size=(0.1, 3.0, 1.5)),
            WallConfig(name="wall_right", position=(1.0, 0.0, 0.75), size=(0.1, 3.0, 1.5)),
            WallConfig(name="wall_center", position=(0.0, 1.0, 0.75), size=(1.5, 0.1, 1.5)),
        ),
        cameras=(
            CameraConfig(name="front_rgbd_camera"),
        ),
    )