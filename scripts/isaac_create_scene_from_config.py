"""Create Isaac Sim scenes from project SceneConfig objects.

This script is intended to run inside the Isaac Sim Python environment on the
remote GPU server.

Examples:

    conda activate /root/autodl-tmp/conda-envs/isaacsim
    export OMNI_KIT_ACCEPT_EULA=YES
    export VK_ICD_FILENAMES=/etc/vulkan/icd.d/nvidia_icd.json

    python scripts/isaac_create_scene_from_config.py --scene default
    python scripts/isaac_create_scene_from_config.py --scene maze
    python scripts/isaac_create_scene_from_config.py --scene maze --save-usd outputs/isaac/simple_maze.usd
"""

from __future__ import annotations

import argparse
import os
import sys
import traceback
from pathlib import Path


COLOR_TO_RGB = {
    "red": (1.0, 0.0, 0.0),
    "blue": (0.0, 0.1, 1.0),
    "green": (0.0, 0.8, 0.1),
}


def main() -> int:
    """Create an Isaac Sim scene from a project SceneConfig."""

    args = _parse_args()

    # Prevent Isaac Sim's SimulationApp from receiving this script's CLI args.
    sys.argv = [sys.argv[0]]

    _print_environment_notes(args.scene)

    try:
        from isaacsim import SimulationApp  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        print(
            "ERROR: Could not import isaacsim. "
            "Activate the Isaac Sim environment before running this script.",
            file=sys.stderr,
        )
        return 1

    print("[1/7] Starting SimulationApp...", flush=True)
    simulation_app = SimulationApp({"headless": True})

    try:
        print("[2/7] Importing Isaac Sim modules...", flush=True)
        from isaacsim.core.api import World  # type: ignore[import-not-found]
        from omni.usd import get_context  # type: ignore[import-not-found]
        from pxr import Gf, UsdGeom  # type: ignore[import-not-found]

        from cosmos_vla_drone.isaac_env.scene_config import (
            create_default_scene_config,
            create_maze_scene_config,
        )

        scene_config = _load_scene_config(
            args.scene,
            create_default_scene_config,
            create_maze_scene_config,
        )

        print(f"[3/7] Creating world for scene: {scene_config.name}", flush=True)
        world = World()
        world.scene.add_default_ground_plane()
        stage = get_context().get_stage()

        print("[4/7] Creating targets...", flush=True)
        _create_targets(stage, scene_config, UsdGeom, Gf, args.target_radius)

        print("[5/7] Creating walls...", flush=True)
        _create_walls(stage, scene_config, UsdGeom, Gf)

        print("[6/7] Resetting and stepping simulation...", flush=True)
        world.reset()
        for _ in range(args.steps):
            world.step(render=False)

        if args.save_usd is not None:
            save_path = Path(args.save_usd)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            get_context().save_as_stage(str(save_path))
            print(f"Saved USD scene to: {save_path}", flush=True)

        print("[7/7] Closing SimulationApp...", flush=True)

    except BaseException:
        print("ERROR: Isaac Sim scene creation failed.", file=sys.stderr)
        traceback.print_exc()
        return_code = 1
    else:
        return_code = 0
    finally:
        simulation_app.close()

    if return_code == 0:
        print("Isaac Sim scene creation from config OK", flush=True)

    return return_code


def _load_scene_config(
    scene_name: str,
    create_default_scene_config,
    create_maze_scene_config,
):
    if scene_name == "default":
        return create_default_scene_config()
    if scene_name == "maze":
        return create_maze_scene_config()
    raise ValueError(f"Unsupported scene: {scene_name}")


def _create_targets(stage, scene_config, UsdGeom, Gf, target_radius: float) -> None:
    UsdGeom.Xform.Define(stage, "/World/Targets")

    for target in scene_config.targets:
        rgb = COLOR_TO_RGB[target.color]
        prim_path = f"/World/Targets/{target.name}"

        sphere = UsdGeom.Sphere.Define(stage, prim_path)
        sphere.CreateRadiusAttr(target_radius)
        sphere.CreateDisplayColorAttr([Gf.Vec3f(*rgb)])

        xform_api = UsdGeom.XformCommonAPI(sphere.GetPrim())
        xform_api.SetTranslate(Gf.Vec3d(*target.position))

        print(
            f"  target={target.name} color={target.color} "
            f"position={target.position}",
            flush=True,
        )


def _create_walls(stage, scene_config, UsdGeom, Gf) -> None:
    if not scene_config.walls:
        print("  no walls in this scene", flush=True)
        return

    UsdGeom.Xform.Define(stage, "/World/Walls")

    for wall in scene_config.walls:
        prim_path = f"/World/Walls/{wall.name}"

        cube = UsdGeom.Cube.Define(stage, prim_path)
        cube.CreateSizeAttr(1.0)
        cube.CreateDisplayColorAttr([Gf.Vec3f(0.55, 0.55, 0.55)])

        xform_api = UsdGeom.XformCommonAPI(cube.GetPrim())
        xform_api.SetTranslate(Gf.Vec3d(*wall.position))
        xform_api.SetScale(Gf.Vec3f(*wall.size))

        print(
            f"  wall={wall.name} position={wall.position} size={wall.size}",
            flush=True,
        )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an Isaac Sim scene from SceneConfig.")
    parser.add_argument(
        "--scene",
        choices=("default", "maze"),
        default="default",
        help="Scene config to instantiate.",
    )
    parser.add_argument(
        "--save-usd",
        default=None,
        help="Optional path for saving the generated USD scene.",
    )
    parser.add_argument(
        "--target-radius",
        type=float,
        default=0.12,
        help="Radius of each colored target sphere.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=10,
        help="Number of simulation steps to run after scene creation.",
    )
    return parser.parse_args()


def _print_environment_notes(scene_name: str) -> None:
    eula = os.getenv("OMNI_KIT_ACCEPT_EULA")
    vulkan_icd = os.getenv("VK_ICD_FILENAMES")

    print("Isaac Sim config scene environment:", flush=True)
    print(f"  scene={scene_name}", flush=True)
    print(f"  OMNI_KIT_ACCEPT_EULA={eula}", flush=True)
    print(f"  VK_ICD_FILENAMES={vulkan_icd}", flush=True)

    if eula != "YES":
        print(
            "WARNING: OMNI_KIT_ACCEPT_EULA is not set to YES. "
            "Isaac Sim may refuse to start.",
            flush=True,
        )

    if not vulkan_icd:
        print(
            "WARNING: VK_ICD_FILENAMES is not set. "
            "On AutoDL, set it to /etc/vulkan/icd.d/nvidia_icd.json "
            "to force Vulkan to use the NVIDIA ICD.",
            flush=True,
        )


if __name__ == "__main__":
    raise SystemExit(main())