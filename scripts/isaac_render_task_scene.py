"""Render a richer Isaac Sim drone task scene.

This script creates a small maze-like drone navigation scene with colored
targets, walls, a simple drone placeholder, and an RGB camera view.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


TARGET_COLORS: dict[str, tuple[float, float, float]] = {
    "red": (1.0, 0.05, 0.03),
    "blue": (0.05, 0.25, 1.0),
    "green": (0.05, 0.85, 0.2),
    "yellow": (1.0, 0.9, 0.05),
    "gray": (0.55, 0.55, 0.55),
    "dark_gray": (0.18, 0.18, 0.18),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scene",
        choices=("default", "maze"),
        default="maze",
        help="Scene configuration to render.",
    )
    parser.add_argument(
        "--output",
        default="outputs/isaac/task_scene.png",
        help="Path for the rendered RGB image.",
    )
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--steps", type=int, default=120)
    return parser.parse_args()


def color_for(name: str) -> tuple[float, float, float]:
    return TARGET_COLORS.get(name, TARGET_COLORS["gray"])


def define_cube(
    stage: Any,
    path: str,
    position: tuple[float, float, float],
    scale: tuple[float, float, float],
    color: tuple[float, float, float],
) -> None:
    from pxr import Gf, UsdGeom

    cube = UsdGeom.Cube.Define(stage, path)
    cube.CreateSizeAttr(1.0)
    cube.CreateDisplayColorAttr([Gf.Vec3f(*color)])
    xform = UsdGeom.XformCommonAPI(cube)
    xform.SetTranslate(Gf.Vec3d(*position))
    xform.SetScale(Gf.Vec3f(*scale))


def define_sphere(
    stage: Any,
    path: str,
    position: tuple[float, float, float],
    radius: float,
    color: tuple[float, float, float],
) -> None:
    from pxr import Gf, UsdGeom

    sphere = UsdGeom.Sphere.Define(stage, path)
    sphere.CreateRadiusAttr(radius)
    sphere.CreateDisplayColorAttr([Gf.Vec3f(*color)])
    xform = UsdGeom.XformCommonAPI(sphere)
    xform.SetTranslate(Gf.Vec3d(*position))


def define_cylinder(
    stage: Any,
    path: str,
    position: tuple[float, float, float],
    radius: float,
    height: float,
    color: tuple[float, float, float],
) -> None:
    from pxr import Gf, UsdGeom

    cylinder = UsdGeom.Cylinder.Define(stage, path)
    cylinder.CreateRadiusAttr(radius)
    cylinder.CreateHeightAttr(height)
    cylinder.CreateDisplayColorAttr([Gf.Vec3f(*color)])
    xform = UsdGeom.XformCommonAPI(cylinder)
    xform.SetTranslate(Gf.Vec3d(*position))


def add_lighting(stage: Any) -> None:
    from pxr import Gf, UsdLux

    dome = UsdLux.DomeLight.Define(stage, "/World/Lights/DomeLight")
    dome.CreateIntensityAttr(700.0)
    dome.CreateColorAttr(Gf.Vec3f(0.9, 0.95, 1.0))

    sun = UsdLux.DistantLight.Define(stage, "/World/Lights/Sun")
    sun.CreateIntensityAttr(2500.0)
    sun.CreateAngleAttr(0.45)
    sun.CreateColorAttr(Gf.Vec3f(1.0, 0.96, 0.86))


def add_task_labels_as_markers(stage: Any) -> None:
    """Add small marker posts so the task layout is readable from camera."""

    define_cylinder(
        stage,
        "/World/Markers/StartPost",
        (-2.4, -2.4, 0.45),
        radius=0.05,
        height=0.9,
        color=(1.0, 1.0, 1.0),
    )
    define_sphere(
        stage,
        "/World/Markers/GoalBeacon",
        (0.0, -2.0, 0.65),
        radius=0.18,
        color=(1.0, 0.9, 0.05),
    )


def add_drone_placeholder(stage: Any) -> None:
    """Create a simple drone-like placeholder at the start position."""

    body_position = (-2.4, -2.4, 0.85)
    body_color = (0.12, 0.12, 0.14)
    arm_color = (0.8, 0.8, 0.85)
    rotor_color = (0.02, 0.02, 0.02)

    define_cube(
        stage,
        "/World/Drone/Body",
        body_position,
        scale=(0.28, 0.18, 0.08),
        color=body_color,
    )
    define_cube(
        stage,
        "/World/Drone/ArmX",
        body_position,
        scale=(0.75, 0.035, 0.025),
        color=arm_color,
    )
    define_cube(
        stage,
        "/World/Drone/ArmY",
        body_position,
        scale=(0.035, 0.75, 0.025),
        color=arm_color,
    )

    rotor_offsets = [
        (0.42, 0.42, 0.03),
        (0.42, -0.42, 0.03),
        (-0.42, 0.42, 0.03),
        (-0.42, -0.42, 0.03),
    ]
    for index, offset in enumerate(rotor_offsets):
        define_cylinder(
            stage,
            f"/World/Drone/Rotor_{index}",
            (
                body_position[0] + offset[0],
                body_position[1] + offset[1],
                body_position[2] + offset[2],
            ),
            radius=0.16,
            height=0.025,
            color=rotor_color,
        )


def add_scene_from_config(stage: Any, scene_name: str) -> None:
    from cosmos_vla_drone.isaac_env.scene_config import (
        create_default_scene_config,
        create_maze_scene_config,
    )

    scene_config = (
        create_maze_scene_config()
        if scene_name == "maze"
        else create_default_scene_config()
    )

    for target in scene_config.targets:
        define_sphere(
            stage,
            f"/World/Targets/{target.name}",
            target.position,
            radius=0.22,
            color=color_for(target.color),
        )
        define_cylinder(
            stage,
            f"/World/Targets/{target.name}_stand",
            (target.position[0], target.position[1], 0.25),
            radius=0.04,
            height=0.5,
            color=color_for(target.color),
        )

    for wall in scene_config.walls:
        define_cube(
            stage,
            f"/World/Walls/{wall.name}",
            wall.position,
            wall.size,
            color=(0.45, 0.47, 0.5),
        )

def look_at_quat(
    camera_position: np.ndarray,
    target_position: np.ndarray,
) -> np.ndarray:
    """Return a camera quaternion that looks from camera_position to target_position."""

    from scipy.spatial.transform import Rotation

    forward = target_position - camera_position
    forward = forward / np.linalg.norm(forward)

    world_up = np.array([0.0, 0.0, 1.0])
    right = np.cross(forward, world_up)
    right = right / np.linalg.norm(right)

    up = np.cross(right, forward)
    up = up / np.linalg.norm(up)

    rotation_matrix = np.eye(3)
    rotation_matrix[:, 0] = right
    rotation_matrix[:, 1] = up
    rotation_matrix[:, 2] = -forward

    quat_xyzw = Rotation.from_matrix(rotation_matrix).as_quat()
    return np.array([quat_xyzw[3], quat_xyzw[0], quat_xyzw[1], quat_xyzw[2]])

def save_rgb(camera: Any, output_path: Path) -> None:
    rgba = camera.get_rgba()
    if rgba is None:
        raise RuntimeError("Camera returned None for RGBA frame.")

    rgb = np.asarray(rgba)
    if rgb.ndim != 3 or rgb.shape[2] < 3:
        raise RuntimeError(f"Unexpected camera frame shape: {rgb.shape}")

    rgb = rgb[:, :, :3]
    if rgb.dtype != np.uint8:
        rgb = np.clip(rgb * 255.0, 0, 255).astype(np.uint8)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgb).save(output_path)
    print(f"Saved task scene image to: {output_path}")
    print(f"Image shape: {rgb.shape}")


def main() -> None:
    args = parse_args()

    os.environ.setdefault("OMNI_KIT_ACCEPT_EULA", "YES")

    print("Isaac Sim task scene render environment:")
    print(f"  scene={args.scene}")
    print(f"  output={args.output}")
    print(f"  OMNI_KIT_ACCEPT_EULA={os.environ.get('OMNI_KIT_ACCEPT_EULA')}")
    print(f"  VK_ICD_FILENAMES={os.environ.get('VK_ICD_FILENAMES', '')}")

    # Prevent script arguments from being forwarded to Kit.
    sys.argv = [sys.argv[0]]

    print("[1/8] Starting SimulationApp...", flush=True)
    from isaacsim import SimulationApp

    simulation_app = SimulationApp(
        {
            "headless": True,
            "width": args.width,
            "height": args.height,
        }
    )

    try:
        print("[2/8] Importing Isaac Sim modules...", flush=True)
        from isaacsim.core.api import World
        from isaacsim.sensors.camera import Camera
        from pxr import Gf, UsdGeom

        print("[3/8] Creating world...", flush=True)
        world = World()
        world.scene.add_default_ground_plane()
        stage = world.stage

        UsdGeom.Xform.Define(stage, "/World/Targets")
        UsdGeom.Xform.Define(stage, "/World/Walls")
        UsdGeom.Xform.Define(stage, "/World/Drone")
        UsdGeom.Xform.Define(stage, "/World/Markers")
        UsdGeom.Xform.Define(stage, "/World/Lights")

        print("[4/8] Adding maze, targets, drone, and lights...", flush=True)
        add_lighting(stage)
        add_scene_from_config(stage, args.scene)
        add_drone_placeholder(stage)
        add_task_labels_as_markers(stage)

        print("[5/8] Creating overview camera...", flush=True)
        camera = Camera(
            prim_path="/World/TaskCamera",
            position=camera_position,
            frequency=20,
            resolution=(args.width, args.height),
        )
        camera.set_world_pose(
            position=camera_position,
            orientation=camera_orientation,
        )
        camera.initialize()

        print("[6/8] Resetting and stepping simulation...", flush=True)
        world.reset()
        for _ in range(args.steps):
            world.step(render=True)

        print("[7/8] Capturing RGB frame...", flush=True)
        save_rgb(camera, Path(args.output))

    finally:
        print("[8/8] Closing SimulationApp...", flush=True)
        simulation_app.close()


if __name__ == "__main__":
    main()