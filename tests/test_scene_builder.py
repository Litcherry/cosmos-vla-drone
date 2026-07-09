from cosmos_vla_drone.isaac_env.scene_builder import SceneBuilder
from cosmos_vla_drone.isaac_env.scene_config import (
    create_default_scene_config,
    create_maze_scene_config,
)


def test_scene_builder_creates_default_scene_plan():
    builder = SceneBuilder()
    scene = create_default_scene_config()

    plan = builder.create_build_plan(scene)

    assert plan.scene_name == "default_colored_target_scene"
    assert [step.kind for step in plan.steps] == [
        "ground_plane",
        "drone",
        "target",
        "target",
        "target",
        "camera",
    ]


def test_scene_builder_includes_target_details():
    builder = SceneBuilder()
    scene = create_default_scene_config()

    plan = builder.create_build_plan(scene)
    red_target_step = next(step for step in plan.steps if step.name == "red_target")

    assert red_target_step.kind == "target"
    assert red_target_step.details["color"] == "red"
    assert red_target_step.details["position"] == (1.5, 0.8, 0.0)


def test_scene_builder_includes_maze_walls():
    builder = SceneBuilder()
    scene = create_maze_scene_config()

    plan = builder.create_build_plan(scene)
    wall_steps = [step for step in plan.steps if step.kind == "wall"]

    assert len(wall_steps) == 3
    assert {step.name for step in wall_steps} == {"wall_left", "wall_right", "wall_center"}