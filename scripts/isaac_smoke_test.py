"""Headless Isaac Sim smoke test for remote GPU servers.

This script is intended to run inside the Isaac Sim Python environment, not the
regular project development environment.

Example:

    conda activate /root/autodl-tmp/conda-envs/isaacsim
    export OMNI_KIT_ACCEPT_EULA=YES
    export VK_ICD_FILENAMES=/etc/vulkan/icd.d/nvidia_icd.json
    python scripts/isaac_smoke_test.py
"""

from __future__ import annotations

import os
import sys


def main() -> int:
    """Run a minimal Isaac Sim headless world test."""

    _print_environment_notes()

    try:
        from isaacsim import SimulationApp # type: ignore[import-not-found]
    except ModuleNotFoundError:
        print(
            "ERROR: Could not import isaacsim. "
            "Activate the Isaac Sim environment before running this script.",
            file=sys.stderr,
        )
        return 1

    print("[1/5] Starting SimulationApp...", flush=True)
    simulation_app = SimulationApp({"headless": True})

    try:
        print("[2/5] Importing World...", flush=True)
        from isaacsim.core.api import World  # type: ignore[import-not-found]

        print("[3/5] Creating world and ground plane...", flush=True)
        world = World()
        world.scene.add_default_ground_plane()
        world.reset()

        print("[4/5] Stepping simulation...", flush=True)
        for _ in range(10):
            world.step(render=False)

        print("[5/5] Closing SimulationApp...", flush=True)
    finally:
        simulation_app.close()

    print("Isaac Sim empty world smoke test OK", flush=True)
    return 0


def _print_environment_notes() -> None:
    eula = os.getenv("OMNI_KIT_ACCEPT_EULA")
    vulkan_icd = os.getenv("VK_ICD_FILENAMES")

    print("Isaac Sim smoke test environment:", flush=True)
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