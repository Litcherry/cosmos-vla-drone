from cosmos_vla_drone.isaac_env.scene_config import (
    CameraConfig,
    DroneConfig,
    SceneConfig,
    TargetConfig,
    WallConfig,
    create_default_scene_config,
    create_maze_scene_config,
)


def test_default_scene_config_contains_colored_targets():
    scene = create_default_scene_config()

    assert scene.name == "default_colored_target_scene"
    assert len(scene.targets) == 3
    assert {target.color for target in scene.targets} == {"red", "blue", "green"}
    assert scene.cameras[0].enable_depth is True


def test_maze_scene_config_contains_walls():
    scene = create_maze_scene_config()

    assert scene.name == "simple_maze_scene"
    assert len(scene.walls) == 3
    assert {wall.name for wall in scene.walls} == {"wall_left", "wall_right", "wall_center"}


def test_scene_config_can_be_customized():
    scene = SceneConfig(
        name="custom_scene",
        drone=DroneConfig(initial_position=(0.0, 0.0, 1.0), max_speed=2.0),
        targets=(
            TargetConfig(name="test_target", color="red", position=(1.0, 1.0, 0.0)),
        ),
        walls=(
            WallConfig(name="test_wall", position=(0.0, 1.0, 0.5), size=(1.0, 0.1, 1.0)),
        ),
        cameras=(
            CameraConfig(name="test_camera", resolution=(320, 240), enable_depth=False),
        ),
    )

    assert scene.drone.initial_position == (0.0, 0.0, 1.0)
    assert scene.drone.max_speed == 2.0
    assert scene.targets[0].name == "test_target"
    assert scene.walls[0].size == (1.0, 0.1, 1.0)
    assert scene.cameras[0].resolution == (320, 240)
    assert scene.cameras[0].enable_depth is False