"""Replay a baseline drone plan inside an Isaac Sim USD scene."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


DEFAULT_INSTRUCTION = "起飞，找到蓝色目标，飞到它上方 1 米处悬停 3 秒，然后降落"

DEFAULT_SCENE_PATH = PROJECT_ROOT / "outputs" / "isaac" / "edited_task_scene.usd"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "outputs" / "isaac" / "replayed_task_scene.usd"
DEFAULT_DRONE_PRIM_PATH = "/World/cf2x"

TARGET_PRIM_PATHS: dict[str, str] = {
    "red": "/World/Targets/red_target",
    "blue": "/World/Targets/blue_target",
    "green": "/World/Targets/green_target",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Replay a baseline plan by moving a Crazyflie prim in Isaac Sim.",
    )
    parser.add_argument("--scene", type=Path, default=DEFAULT_SCENE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--drone-prim-path", default=DEFAULT_DRONE_PRIM_PATH)
    parser.add_argument("--instruction", default=DEFAULT_INSTRUCTION)
    parser.add_argument("--takeoff-altitude", type=float, default=1.5)
    parser.add_argument("--land-z", type=float, default=0.25)
    parser.add_argument("--steps-per-action", type=int, default=30)
    return parser.parse_args()


def interpolate_position(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    steps: int,
) -> list[tuple[float, float, float]]:
    if steps <= 1:
        return [end]

    positions = []
    for index in range(1, steps + 1):
        ratio = index / steps
        positions.append(
            (
                start[0] + (end[0] - start[0]) * ratio,
                start[1] + (end[1] - start[1]) * ratio,
                start[2] + (end[2] - start[2]) * ratio,
            )
        )
    return positions


def get_action_name(action: dict[str, Any]) -> str:
    value = action.get("action")
    if not isinstance(value, str):
        raise ValueError(f"Action has invalid action name: {action}")
    return value


def get_target_name(action: dict[str, Any], last_target: str | None) -> str:
    value = action.get("target", last_target)
    if not isinstance(value, str):
        raise ValueError(f"Action requires a target: {action}")
    return value


def get_world_position(stage: Any, prim_path: str, usd_geom: Any, usd_time_code: Any) -> tuple[float, float, float]:
    prim = stage.GetPrimAtPath(prim_path)
    if not prim.IsValid():
        raise RuntimeError(f"Target prim not found: {prim_path}")

    transform = usd_geom.Xformable(prim).ComputeLocalToWorldTransform(usd_time_code.Default())
    translation = transform.ExtractTranslation()
    return (float(translation[0]), float(translation[1]), float(translation[2]))


def read_target_positions(stage: Any, usd_geom: Any, usd_time_code: Any) -> dict[str, tuple[float, float, float]]:
    target_positions = {
        name: get_world_position(stage, prim_path, usd_geom, usd_time_code)
        for name, prim_path in TARGET_PRIM_PATHS.items()
    }

    print("  target_positions:")
    for name, position in target_positions.items():
        print(f"    {name}: {position}")

    return target_positions


def build_replay_waypoints(
    actions: list[dict[str, Any]],
    *,
    start_position: tuple[float, float, float],
    target_positions: dict[str, tuple[float, float, float]],
    default_takeoff_altitude: float,
    land_z: float,
    steps_per_action: int,
) -> list[tuple[str, tuple[float, float, float]]]:
    current = start_position
    last_target: str | None = None
    waypoints: list[tuple[str, tuple[float, float, float]]] = []

    for action in actions:
        action_name = get_action_name(action)

        if action_name == "takeoff":
            altitude = float(action.get("altitude", default_takeoff_altitude))
            next_position = (current[0], current[1], altitude)
            for position in interpolate_position(current, next_position, steps_per_action):
                waypoints.append((action_name, position))
            current = next_position

        elif action_name == "search":
            last_target = get_target_name(action, last_target)
            if last_target not in target_positions:
                raise ValueError(f"Unknown target: {last_target}")
            waypoints.append((f"search:{last_target}", current))

        elif action_name == "move_above":
            last_target = get_target_name(action, last_target)
            if last_target not in target_positions:
                raise ValueError(f"Unknown target: {last_target}")

            target_x, target_y, target_z = target_positions[last_target]
            height_above_target = float(action.get("height", 1.0))
            next_position = (target_x, target_y, target_z + height_above_target)

            for position in interpolate_position(current, next_position, steps_per_action):
                waypoints.append((f"move_above:{last_target}", position))
            current = next_position

        elif action_name == "hover":
            duration = float(action.get("duration", 1.0))
            repeat_count = max(1, int(duration * 10))
            for _ in range(repeat_count):
                waypoints.append((f"hover:{duration:g}s", current))

        elif action_name == "land":
            next_position = (current[0], current[1], land_z)
            for position in interpolate_position(current, next_position, steps_per_action):
                waypoints.append((action_name, position))
            current = next_position

        else:
            raise ValueError(f"Unsupported action: {action}")

    return waypoints


def main() -> int:
    args = parse_args()

    scene_path = args.scene.resolve()
    output_path = args.output.resolve()

    if not scene_path.exists():
        raise FileNotFoundError(f"Scene file does not exist: {scene_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("Isaac Sim baseline replay environment:")
    print(f"  scene={scene_path}")
    print(f"  output={output_path}")
    print(f"  drone_prim_path={args.drone_prim_path}")

    from isaacsim import SimulationApp

    print("[1/7] Starting SimulationApp...", flush=True)
    simulation_app = SimulationApp({"headless": True})

    try:
        print("[2/7] Importing Isaac Sim modules...", flush=True)
        import omni.usd
        from pxr import Gf, Usd, UsdGeom

        from cosmos_vla_drone.baseline.runner import run_baseline_task

        print("[3/7] Opening scene...", flush=True)
        usd_context = omni.usd.get_context()
        if not usd_context.open_stage(str(scene_path)):
            raise RuntimeError(f"Failed to open stage: {scene_path}")

        for _ in range(10):
            simulation_app.update()

        stage = usd_context.get_stage()

        drone_prim = stage.GetPrimAtPath(args.drone_prim_path)
        if not drone_prim.IsValid():
            raise RuntimeError(f"Drone prim not found: {args.drone_prim_path}")

        drone_xform = UsdGeom.Xformable(drone_prim)
        common_api = UsdGeom.XformCommonAPI(drone_prim)

        local_transform = drone_xform.GetLocalTransformation()
        start_translation = local_transform.ExtractTranslation()
        start_position = (
            float(start_translation[0]),
            float(start_translation[1]),
            float(start_translation[2]),
        )
        print(f"  start_position={start_position}")

        target_positions = read_target_positions(stage, UsdGeom, Usd.TimeCode)

        print("[4/7] Planning baseline task...", flush=True)
        plan = run_baseline_task(args.instruction)
        print(f"  instruction={plan.instruction}")
        print(f"  planner_source={plan.planner_source}")
        print(f"  actions={plan.actions}")

        print("[5/7] Replaying waypoints...", flush=True)
        waypoints = build_replay_waypoints(
            plan.actions,
            start_position=start_position,
            target_positions=target_positions,
            default_takeoff_altitude=args.takeoff_altitude,
            land_z=args.land_z,
            steps_per_action=args.steps_per_action,
        )

        for index, (label, position) in enumerate(waypoints, start=1):
            common_api.SetTranslate(Gf.Vec3d(*position))
            simulation_app.update()

            if index == 1 or index == len(waypoints) or index % args.steps_per_action == 0:
                print(f"  waypoint {index:03d}/{len(waypoints):03d}: {label} -> {position}")

        print("[6/7] Saving replayed scene...", flush=True)
        stage.GetRootLayer().Export(str(output_path))
        print(f"  saved={output_path}")

    finally:
        print("[7/7] Closing SimulationApp...", flush=True)
        simulation_app.close()

    print("Isaac Sim baseline replay OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())