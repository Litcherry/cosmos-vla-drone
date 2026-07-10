"""Create a simple Isaac Sim scene with colored target objects.

This script is intended to run inside the Isaac Sim Python environment on the
remote GPU server.

Example:

    conda activate /root/autodl-tmp/conda-envs/isaacsim
    export OMNI_KIT_ACCEPT_EULA=YES
    export VK_ICD_FILENAMES=/etc/vulkan/icd.d/nvidia_icd.json
    python scripts/isaac_create_targets_scene.py

Optional USD export:

    python scripts/isaac_create_targets_scene.py --save-usd outputs/isaac/default_targets.usd
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
    """Create a colored-target Isaac Sim scene."""

    args = _parse_args()

    # Prevent Isaac Sim's SimulationApp from receiving this script's CLI args.
    sys.argv = [sys.argv[0]]

    _print_environment_notes()

    try:
        from isaacsim import SimulationApp  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        print(
            "ERROR: Could not import isaacsim. "
            "Activate the Isaac Sim environment before running this script.",
            file=sys.stderr,
        )
        return 1

    print("[1/6] Starting SimulationApp...", flush=True)
    simulation_app = SimulationApp({"headless": True})

    try:
        print("[2/6] Importing Isaac Sim modules...", flush=True)
        from isaacsim.core.api import World  # type: ignore[import-not-found]
        from omni.usd import get_context  # type: ignore[import-not-found]
        from pxr import Gf, UsdGeom  # type: ignore[import-not-found]

        from cosmos_vla_drone.isaac_env.scene_config import create_default_scene_config

        print("[3/6] Creating world and ground plane...", flush=True)
        world = World()
        world.scene.add_default_ground_plane()

        scene_config = create_default_scene_config()
        stage = get_context().get_stage()

        print("[4/6] Creating colored targets...", flush=True)
        UsdGeom.Xform.Define(stage, "/World/Targets")

        for target in scene_config.targets:
            rgb = COLOR_TO_RGB[target.color]
            prim_path = f"/World/Targets/{target.name}"

            sphere = UsdGeom.Sphere.Define(stage, prim_path)
            sphere.CreateRadiusAttr(args.target_radius)
            sphere.CreateDisplayColorAttr([Gf.Vec3f(*rgb)])

            xform_api = UsdGeom.XformCommonAPI(sphere.GetPrim())
            xform_api.SetTranslate(Gf.Vec3d(*target.position))

            print(
                f"  target={target.name} color={target.color} "
                f"position={target.position}",
                flush=True,
            )

        print("[5/6] Resetting and stepping simulation...", flush=True)
        world.reset()
        for _ in range(args.steps):
            world.step(render=False)

        if args.save_usd is not None:
            save_path = Path(args.save_usd)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            get_context().save_as_stage(str(save_path))
            print(f"Saved USD scene to: {save_path}", flush=True)

        print("[6/6] Closing SimulationApp...", flush=True)

    except BaseException:
        print("ERROR: Isaac Sim colored-target scene creation failed.", file=sys.stderr)
        traceback.print_exc()
        return_code = 1
    else:
        return_code = 0
    finally:
        simulation_app.close()

    if return_code == 0:
        print("Isaac Sim colored-target scene creation OK", flush=True)

    return return_code


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a colored-target Isaac Sim scene.")
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


def _print_environment_notes() -> None:
    eula = os.getenv("OMNI_KIT_ACCEPT_EULA")
    vulkan_icd = os.getenv("VK_ICD_FILENAMES")

    print("Isaac Sim scene creation environment:", flush=True)
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