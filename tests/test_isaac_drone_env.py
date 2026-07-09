import pytest

from cosmos_vla_drone.isaac_env.interfaces import DroneEnvironment
from cosmos_vla_drone.isaac_env.isaac_drone_env import (
    IsaacDroneEnvironment,
    IsaacSimUnavailableError,
)
from cosmos_vla_drone.isaac_env.scene_config import create_maze_scene_config


def test_isaac_drone_environment_matches_protocol():
    env = IsaacDroneEnvironment()

    assert isinstance(env, DroneEnvironment)


def test_isaac_drone_environment_can_create_build_plan_without_isaac_sim():
    env = IsaacDroneEnvironment()

    plan = env.create_build_plan()

    assert plan.scene_name == "default_colored_target_scene"
    assert env.build_plan == plan
    assert plan.steps[0].kind == "ground_plane"


def test_isaac_drone_environment_accepts_custom_scene_config():
    env = IsaacDroneEnvironment(scene_config=create_maze_scene_config())

    plan = env.create_build_plan()

    assert plan.scene_name == "simple_maze_scene"
    assert any(step.kind == "wall" for step in plan.steps)


def test_isaac_drone_environment_reports_unavailable_backend_after_build_plan():
    env = IsaacDroneEnvironment()

    with pytest.raises(IsaacSimUnavailableError, match="Isaac Sim is not available"):
        env.initialize()

    assert env.build_plan is not None


def test_isaac_drone_environment_requires_initialization_before_reset():
    env = IsaacDroneEnvironment()

    with pytest.raises(IsaacSimUnavailableError, match="initialize"):
        env.reset()