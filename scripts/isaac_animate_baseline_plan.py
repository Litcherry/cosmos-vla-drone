"""Create a time-sampled Isaac Sim animation from a baseline drone plan."""

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
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "outputs" / "isaac" / "animated_task_scene.usd"
DEFAULT_DRONE_PRIM_PATH = "/World/cf2x"

TARGET_PRIM_PATHS: dict[str, str] = {
    "red": "/World/Targets/red_target",
    "blue": "/World/Targets/blue_target",
    "green": "/World/Targets/green_target",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Animate a Crazyflie prim using baseline planner actions.",
    )
    parser.add_argument("--scene", type=Path, default=DEFAULT_SCENE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--drone-prim-path", default=DEFAULT_DRONE_PRIM_PATH)
    parser.add_argument("--instruction", default=DEFAULT_INSTRUCTION)
    parser.add_argument("--takeoff-altitude", type=float, default=1.5)
    parser.add_argument("--land-z", type=float, default=0.25)
    parser.add_argument("--frames-per-move", type=int, default=60)
    parser.add_argument("--frames-per-second", type=float, default=24.0)
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


def get_world_position(
    stage: Any,
    prim_path: str,
    usd_geom: Any,
    usd_time_code: Any,
) -> tuple[float, float, float]:
    prim = stage.GetPrimAtPath(prim_path)
    if not prim.IsValid():
        raise RuntimeError(f"Target prim not found: {prim_path}")

    transform = usd_geom.Xformable(prim).ComputeLocalToWorldTransform(
        usd_time_code.Default()
    )
    translation = transform.ExtractTranslation()
    return (float(translation[0]), float(translation[1]), float(translation[2]))


def read_target_positions(
    stage: Any,
    usd_geom: Any,
    usd_time_code: Any,
) -> dict[str, tuple[float, float, float]]:
    positions = {
        name: get_world_position(stage, prim_path, usd_geom, usd_time_code)
        for name, prim_path in TARGET_PRIM_PATHS.items()
    }

    print("  target_positions:")
    for name, position in positions.items():
        print(f"    {name}: {position}")

    return positions


def build_waypoints(
    actions: list[dict[str, Any]],
    *,
    start_position: tuple[float, float, float],
    target_positions: dict[str, tuple[float, float, float]],
    takeoff_altitude: float,
    land_z: float,
    frames_per_move: int,
    frames_per_second: float,
) -> list[tuple[str, tuple[float, float, float]]]:
    current = start_position
    last_target: str | None = None
    waypoints: list[tuple[str, tuple[float, float, float]]] = []

    for action in actions:
        action_name = get_action_name(action)

        if action_name == "takeoff":
            altitude = float(action.get("altitude", takeoff_altitude))
            next_position = (current[0], current[1], altitude)
            for position in interpolate_position(current, next_position, frames_per_move):
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

            for position in interpolate_position(current, next_position, frames_per_move):
                waypoints.append((f"move_above:{last_target}", position))
            current = next_position

        elif action_name == "hover":
            duration = float(action.get("duration", 1.0))
            hover_frames = max(1, int(duration * frames_per_second))
            for _ in range(hover_frames):
                waypoints.append((f"hover:{duration:g}s", current))

        elif action_name == "land":
            next_position = (current[0], current[1], land_z)
            for position in interpolate_position(current, next_position, frames_per_move):
                waypoints.append((action_name, position))
            current = next_position

        else:
            raise ValueError(f"Unsupported action: {action}")

    return waypoints


def get_or_create_translate_op(drone_prim: Any, usd_geom: Any) -> Any:
    xformable = usd_geom.Xformable(drone_prim)
    for op in xformable.GetOrderedXformOps():
        if op.GetOpType() == usd_geom.XformOp.TypeTranslate:
            return op
    return xformable.AddTranslateOp()


def main() -> int:
    args = parse_args()

    scene_path = args.scene.resolve()
    output_path = args.output.resolve()

    if not scene_path.exists():
        raise FileNotFoundError(f"Scene file does not exist: {scene_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("Isaac Sim baseline animation environment:")
    print(f"  scene={scene_path}")
    print(f"  output={output_path}")
    print(f"  drone_prim_path={args.drone_prim_path}")

    from isaacsim import SimulationApp

    print("[1/8] Starting SimulationApp...", flush=True)
    simulation_app = SimulationApp({"headless": True})

    try:
        print("[2/8] Importing Isaac Sim modules...", flush=True)
        import omni.usd
        from pxr import Gf, Usd, UsdGeom

        from cosmos_vla_drone.baseline.runner import run_baseline_task

        print("[3/8] Opening scene...", flush=True)
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
        local_transform = drone_xform.GetLocalTransformation()
        start_translation = local_transform.ExtractTranslation()
        start_position = (
            float(start_translation[0]),
            float(start_translation[1]),
            float(start_translation[2]),
        )
        print(f"  start_position={start_position}")

        target_positions = read_target_positions(stage, UsdGeom, Usd.TimeCode)

        print("[4/8] Planning baseline task...", flush=True)
        plan = run_baseline_task(args.instruction)
        print(f"  instruction={plan.instruction}")
        print(f"  planner_source={plan.planner_source}")
        print(f"  actions={plan.actions}")

        print("[5/8] Building animation waypoints...", flush=True)
        waypoints = build_waypoints(
            plan.actions,
            start_position=start_position,
            target_positions=target_positions,
            takeoff_altitude=args.takeoff_altitude,
            land_z=args.land_z,
            frames_per_move=args.frames_per_move,
            frames_per_second=args.frames_per_second,
        )
        print(f"  frames={len(waypoints)}")

        print("[6/8] Writing USD time samples...", flush=True)
        translate_op = get_or_create_translate_op(drone_prim, UsdGeom)

        start_frame = 1
        end_frame = max(start_frame, len(waypoints))

        stage.SetStartTimeCode(start_frame)
        stage.SetEndTimeCode(end_frame)
        stage.SetTimeCodesPerSecond(args.frames_per_second)
        stage.SetFramesPerSecond(args.frames_per_second)

        for frame_index, (label, position) in enumerate(waypoints, start=start_frame):
            translate_op.Set(Gf.Vec3d(*position), Usd.TimeCode(frame_index))

            if (
                frame_index == start_frame
                or frame_index == end_frame
                or frame_index % args.frames_per_move == 0
            ):
                print(
                    f"  frame {frame_index:03d}/{end_frame:03d}: "
                    f"{label} -> {position}"
                )

        print("[7/8] Saving animated scene...", flush=True)
        stage.GetRootLayer().Export(str(output_path))
        print(f"  saved={output_path}")

    finally:
        print("[8/8] Closing SimulationApp...", flush=True)
        simulation_app.close()

    print("Isaac Sim baseline animation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())