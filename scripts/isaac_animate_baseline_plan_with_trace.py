"""Create an Isaac Sim baseline animation with trajectory markers and JSON result."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


DEFAULT_INSTRUCTION = "起飞，找到蓝色目标，飞到它上方 1 米处悬停 3 秒，然后降落"
DEFAULT_SCENE_PATH = PROJECT_ROOT / "outputs" / "isaac" / "edited_task_scene.usd"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "outputs" / "isaac" / "animated_task_scene_with_trace.usd"
DEFAULT_DRONE_PRIM_PATH = "/World/cf2x"

TARGET_PRIM_PATHS: dict[str, str] = {
    "red": "/World/Targets/red_target",
    "blue": "/World/Targets/blue_target",
    "green": "/World/Targets/green_target",
}


@dataclass(frozen=True)
class FrameSample:
    label: str
    position: tuple[float, float, float]


@dataclass(frozen=True)
class ActionFrameRange:
    label: str
    start_frame: int
    end_frame: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Animate a Crazyflie prim, add trajectory markers, and write JSON results.",
    )
    parser.add_argument("--scene", type=Path, default=DEFAULT_SCENE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument(
        "--result-json",
        type=Path,
        default=None,
        help="JSON result path. Defaults to output USD stem + '_result.json'.",
    )
    parser.add_argument("--drone-prim-path", default=DEFAULT_DRONE_PRIM_PATH)
    parser.add_argument("--instruction", default=DEFAULT_INSTRUCTION)
    parser.add_argument("--takeoff-altitude", type=float, default=1.5)
    parser.add_argument("--land-z", type=float, default=0.25)
    parser.add_argument("--frames-per-move", type=int, default=60)
    parser.add_argument("--frames-per-second", type=float, default=24.0)
    parser.add_argument("--trace-every-n-frames", type=int, default=8)
    parser.add_argument("--trace-radius", type=float, default=0.045)
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


def append_action_samples(
    *,
    samples: list[FrameSample],
    ranges: list[ActionFrameRange],
    label: str,
    positions: list[tuple[float, float, float]],
) -> None:
    start_frame = len(samples) + 1
    for position in positions:
        samples.append(FrameSample(label=label, position=position))
    end_frame = len(samples)
    ranges.append(ActionFrameRange(label=label, start_frame=start_frame, end_frame=end_frame))


def build_animation_samples(
    actions: list[dict[str, Any]],
    *,
    start_position: tuple[float, float, float],
    target_positions: dict[str, tuple[float, float, float]],
    takeoff_altitude: float,
    land_z: float,
    frames_per_move: int,
    frames_per_second: float,
) -> tuple[list[FrameSample], list[ActionFrameRange]]:
    current = start_position
    last_target: str | None = None
    samples: list[FrameSample] = []
    ranges: list[ActionFrameRange] = []

    for action in actions:
        action_name = get_action_name(action)

        if action_name == "takeoff":
            altitude = float(action.get("altitude", takeoff_altitude))
            next_position = (current[0], current[1], altitude)
            append_action_samples(
                samples=samples,
                ranges=ranges,
                label="takeoff",
                positions=interpolate_position(current, next_position, frames_per_move),
            )
            current = next_position

        elif action_name == "search":
            last_target = get_target_name(action, last_target)
            if last_target not in target_positions:
                raise ValueError(f"Unknown target: {last_target}")
            append_action_samples(
                samples=samples,
                ranges=ranges,
                label=f"search:{last_target}",
                positions=[current],
            )

        elif action_name == "move_above":
            last_target = get_target_name(action, last_target)
            if last_target not in target_positions:
                raise ValueError(f"Unknown target: {last_target}")

            target_x, target_y, target_z = target_positions[last_target]
            height_above_target = float(action.get("height", 1.0))
            next_position = (target_x, target_y, target_z + height_above_target)
            append_action_samples(
                samples=samples,
                ranges=ranges,
                label=f"move_above:{last_target}",
                positions=interpolate_position(current, next_position, frames_per_move),
            )
            current = next_position

        elif action_name == "hover":
            duration = float(action.get("duration", 1.0))
            hover_frames = max(1, int(duration * frames_per_second))
            append_action_samples(
                samples=samples,
                ranges=ranges,
                label=f"hover:{duration:g}s",
                positions=[current for _ in range(hover_frames)],
            )

        elif action_name == "land":
            next_position = (current[0], current[1], land_z)
            append_action_samples(
                samples=samples,
                ranges=ranges,
                label="land",
                positions=interpolate_position(current, next_position, frames_per_move),
            )
            current = next_position

        else:
            raise ValueError(f"Unsupported action: {action}")

    return samples, ranges


def get_or_create_translate_op(drone_prim: Any, usd_geom: Any) -> Any:
    xformable = usd_geom.Xformable(drone_prim)
    for op in xformable.GetOrderedXformOps():
        if op.GetOpType() == usd_geom.XformOp.TypeTranslate:
            return op
    return xformable.AddTranslateOp()


def trace_color_for_label(label: str) -> tuple[float, float, float]:
    if label.startswith("takeoff"):
        return (1.0, 0.65, 0.0)
    if label.startswith("search"):
        return (0.85, 0.85, 0.2)
    if label.startswith("move_above"):
        return (0.1, 0.45, 1.0)
    if label.startswith("hover"):
        return (0.15, 1.0, 0.35)
    if label.startswith("land"):
        return (1.0, 0.2, 0.2)
    return (1.0, 1.0, 1.0)


def add_trajectory_markers(
    *,
    stage: Any,
    samples: list[FrameSample],
    trace_every_n_frames: int,
    trace_radius: float,
    usd_geom: Any,
    gf: Any,
) -> int:
    trajectory_path = "/World/Trajectory"
    if stage.GetPrimAtPath(trajectory_path).IsValid():
        stage.RemovePrim(trajectory_path)

    usd_geom.Xform.Define(stage, trajectory_path)

    interval = max(1, trace_every_n_frames)
    marker_index = 0

    for frame_index, sample in enumerate(samples, start=1):
        if frame_index != 1 and frame_index != len(samples) and frame_index % interval != 0:
            continue

        marker_index += 1
        marker_path = f"{trajectory_path}/point_{marker_index:03d}"
        sphere = usd_geom.Sphere.Define(stage, marker_path)
        sphere.CreateRadiusAttr(trace_radius)

        marker_xform = usd_geom.XformCommonAPI(sphere.GetPrim())
        marker_xform.SetTranslate(gf.Vec3d(*sample.position))

        color = trace_color_for_label(sample.label)
        sphere.CreateDisplayColorAttr([gf.Vec3f(*color)])

    print(f"  trajectory_markers={marker_index}")
    return marker_index


def print_action_frame_ranges(ranges: list[ActionFrameRange]) -> None:
    print("  action_frame_ranges:")
    for item in ranges:
        print(f"    {item.label}: frames {item.start_frame}-{item.end_frame}")


def tuple_to_list(value: tuple[float, float, float]) -> list[float]:
    return [float(value[0]), float(value[1]), float(value[2])]


def write_result_json(
    *,
    result_path: Path,
    instruction: str,
    planner_source: str,
    actions: list[dict[str, Any]],
    target_positions: dict[str, tuple[float, float, float]],
    start_position: tuple[float, float, float],
    final_position: tuple[float, float, float],
    frame_count: int,
    frames_per_second: float,
    action_frame_ranges: list[ActionFrameRange],
    scene_path: Path,
    output_usd_path: Path,
    drone_prim_path: str,
    trajectory_marker_count: int,
) -> None:
    result = {
        "instruction": instruction,
        "planner_source": planner_source,
        "actions": actions,
        "target_positions": {
            name: tuple_to_list(position) for name, position in target_positions.items()
        },
        "start_position": tuple_to_list(start_position),
        "final_position": tuple_to_list(final_position),
        "frame_count": frame_count,
        "frames_per_second": frames_per_second,
        "duration_seconds": frame_count / frames_per_second if frames_per_second else 0.0,
        "action_frame_ranges": [asdict(item) for item in action_frame_ranges],
        "scene_path": str(scene_path),
        "output_usd_path": str(output_usd_path),
        "drone_prim_path": drone_prim_path,
        "trajectory_marker_count": trajectory_marker_count,
    }

    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"  result_json={result_path}")


def main() -> int:
    args = parse_args()

    scene_path = args.scene.resolve()
    output_path = args.output.resolve()
    result_path = (
        args.result_json.resolve()
        if args.result_json is not None
        else output_path.with_name(f"{output_path.stem}_result.json")
    )

    if not scene_path.exists():
        raise FileNotFoundError(f"Scene file does not exist: {scene_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("Isaac Sim baseline animation with trace environment:")
    print(f"  scene={scene_path}")
    print(f"  output={output_path}")
    print(f"  result_json={result_path}")
    print(f"  drone_prim_path={args.drone_prim_path}")

    from isaacsim import SimulationApp

    print("[1/10] Starting SimulationApp...", flush=True)
    simulation_app = SimulationApp({"headless": True})

    try:
        print("[2/10] Importing Isaac Sim modules...", flush=True)
        import omni.usd
        from pxr import Gf, Usd, UsdGeom

        from cosmos_vla_drone.baseline.runner import run_baseline_task

        print("[3/10] Opening scene...", flush=True)
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
        start_translation = drone_xform.GetLocalTransformation().ExtractTranslation()
        start_position = (
            float(start_translation[0]),
            float(start_translation[1]),
            float(start_translation[2]),
        )
        print(f"  start_position={start_position}")

        target_positions = read_target_positions(stage, UsdGeom, Usd.TimeCode)

        print("[4/10] Planning baseline task...", flush=True)
        plan = run_baseline_task(args.instruction)
        print(f"  instruction={plan.instruction}")
        print(f"  planner_source={plan.planner_source}")
        print(f"  actions={plan.actions}")

        print("[5/10] Building animation samples...", flush=True)
        samples, ranges = build_animation_samples(
            plan.actions,
            start_position=start_position,
            target_positions=target_positions,
            takeoff_altitude=args.takeoff_altitude,
            land_z=args.land_z,
            frames_per_move=args.frames_per_move,
            frames_per_second=args.frames_per_second,
        )
        print(f"  frames={len(samples)}")
        print_action_frame_ranges(ranges)

        print("[6/10] Writing drone time samples...", flush=True)
        translate_op = get_or_create_translate_op(drone_prim, UsdGeom)

        start_frame = 1
        end_frame = max(start_frame, len(samples))

        stage.SetStartTimeCode(start_frame)
        stage.SetEndTimeCode(end_frame)
        stage.SetTimeCodesPerSecond(args.frames_per_second)
        stage.SetFramesPerSecond(args.frames_per_second)

        for frame_index, sample in enumerate(samples, start=start_frame):
            translate_op.Set(Gf.Vec3d(*sample.position), Usd.TimeCode(frame_index))

        print("[7/10] Adding trajectory markers...", flush=True)
        marker_count = add_trajectory_markers(
            stage=stage,
            samples=samples,
            trace_every_n_frames=args.trace_every_n_frames,
            trace_radius=args.trace_radius,
            usd_geom=UsdGeom,
            gf=Gf,
        )

        print("[8/10] Saving animated scene with trace...", flush=True)
        stage.GetRootLayer().Export(str(output_path))
        print(f"  saved={output_path}")

        print("[9/10] Writing JSON result...", flush=True)
        final_position = samples[-1].position if samples else start_position
        write_result_json(
            result_path=result_path,
            instruction=plan.instruction,
            planner_source=plan.planner_source,
            actions=plan.actions,
            target_positions=target_positions,
            start_position=start_position,
            final_position=final_position,
            frame_count=len(samples),
            frames_per_second=args.frames_per_second,
            action_frame_ranges=ranges,
            scene_path=scene_path,
            output_usd_path=output_path,
            drone_prim_path=args.drone_prim_path,
            trajectory_marker_count=marker_count,
        )

    finally:
        print("[10/10] Closing SimulationApp...", flush=True)
        simulation_app.close()

    print("Isaac Sim baseline animation with trace OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())