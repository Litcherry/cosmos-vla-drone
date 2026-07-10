"""Minimal Isaac Sim RGB camera smoke test.

This script checks whether the current server can produce a camera image from
an Isaac Sim scene. It is expected to run inside the Isaac Sim environment.

Example:

    conda activate /root/autodl-tmp/conda-envs/isaacsim
    export OMNI_KIT_ACCEPT_EULA=YES
    export VK_ICD_FILENAMES=/etc/vulkan/icd.d/nvidia_icd.json
    python scripts/isaac_camera_smoke_test.py --output outputs/isaac/camera_smoke.png
"""

from __future__ import annotations

import argparse
import os
import sys
import traceback
from pathlib import Path


def main() -> int:
    args = _parse_args()
    sys.argv = [sys.argv[0]]
    _print_environment_notes(args.output)

    try:
        from isaacsim import SimulationApp  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        print(
            "ERROR: Could not import isaacsim. Activate the Isaac Sim environment first.",
            file=sys.stderr,
        )
        return 1

    print("[1/7] Starting SimulationApp...", flush=True)
    simulation_app = SimulationApp({"headless": True})

    try:
        print("[2/7] Importing Isaac Sim modules...", flush=True)
        import numpy as np
        from isaacsim.core.api import World  # type: ignore[import-not-found]
        from isaacsim.sensors.camera import Camera  # type: ignore[import-not-found]
        from PIL import Image
        from pxr import Gf, UsdGeom  # type: ignore[import-not-found]

        print("[3/7] Creating world and objects...", flush=True)
        world = World()
        world.scene.add_default_ground_plane()
        stage = world.stage

        sphere = UsdGeom.Sphere.Define(stage, "/World/Target/red_target")
        sphere.CreateRadiusAttr(0.25)
        sphere.CreateDisplayColorAttr([Gf.Vec3f(1.0, 0.0, 0.0)])
        UsdGeom.XformCommonAPI(sphere.GetPrim()).SetTranslate(Gf.Vec3d(1.5, 0.0, 0.25))

        print("[4/7] Creating camera...", flush=True)
        camera = Camera(
            prim_path="/World/Camera/front_camera",
            position=np.array([0.0, -3.0, 1.2]),
            orientation=np.array([0.707, 0.0, 0.0, 0.707]),
            resolution=(640, 480),
        )
        camera.initialize()

        print("[5/7] Resetting and stepping simulation...", flush=True)
        world.reset()
        for _ in range(args.steps):
            world.step(render=True)

        print("[6/7] Capturing RGB frame...", flush=True)
        rgba = camera.get_rgba()

        if rgba is None:
            raise RuntimeError("Camera returned None for RGBA frame.")

        rgb = np.asarray(rgba)[..., :3]
        rgb_uint8 = np.clip(rgb * 255.0, 0, 255).astype(np.uint8)

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(rgb_uint8).save(output_path)

        print(f"Saved RGB camera image to: {output_path}", flush=True)
        print(f"Image shape: {rgb_uint8.shape}", flush=True)

        print("[7/7] Closing SimulationApp...", flush=True)

    except BaseException:
        print("ERROR: Isaac Sim camera smoke test failed.", file=sys.stderr)
        traceback.print_exc()
        return_code = 1
    else:
        return_code = 0
    finally:
        simulation_app.close()

    if return_code == 0:
        print("Isaac Sim RGB camera smoke test OK", flush=True)

    return return_code


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an Isaac Sim RGB camera smoke test.")
    parser.add_argument(
        "--output",
        default="outputs/isaac/camera_smoke.png",
        help="Output image path.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=30,
        help="Number of render steps before capturing the frame.",
    )
    return parser.parse_args()


def _print_environment_notes(output: str) -> None:
    print("Isaac Sim camera smoke test environment:", flush=True)
    print(f"  output={output}", flush=True)
    print(f"  OMNI_KIT_ACCEPT_EULA={os.getenv('OMNI_KIT_ACCEPT_EULA')}", flush=True)
    print(f"  VK_ICD_FILENAMES={os.getenv('VK_ICD_FILENAMES')}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())