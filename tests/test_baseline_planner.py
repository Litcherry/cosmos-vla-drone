import pytest

from cosmos_vla_drone.baseline.planner import parse_instruction
from cosmos_vla_drone.baseline.planner_backend import plan_instruction


def test_parse_chinese_red_target_task():
    instruction = "起飞，找到红色目标，飞到它上方 1 米处悬停 5 秒，然后降落"

    actions = parse_instruction(instruction)

    assert actions == [
        {"action": "takeoff", "altitude": 1.5},
        {"action": "search", "target": "red"},
        {"action": "move_above", "target": "red", "height": 1.0},
        {"action": "hover", "duration": 5.0},
        {"action": "land"},
    ]


def test_parse_english_blue_target_task():
    instruction = "take off, find the blue target, move above it 1 meter, hover 3 seconds, then land"

    actions = parse_instruction(instruction)

    assert actions == [
        {"action": "takeoff", "altitude": 1.5},
        {"action": "search", "target": "blue"},
        {"action": "move_above", "target": "blue", "height": 1.0},
        {"action": "hover", "duration": 3.0},
        {"action": "land"},
    ]


def test_parse_green_target_with_default_hover_duration():
    instruction = "起飞，搜索绿色目标，飞到绿色目标上方，然后悬停，最后降落"

    actions = parse_instruction(instruction)

    assert {"action": "search", "target": "green"} in actions
    assert {"action": "hover", "duration": 5.0} in actions


def test_parse_english_move_to_task():
    instruction = "take off, move to x=1 y=-1 z=1.2, hover 2 seconds, then land"

    actions = parse_instruction(instruction)

    assert actions == [
        {"action": "takeoff", "altitude": 1.5},
        {"action": "move_to", "position": (1.0, -1.0, 1.2)},
        {"action": "hover", "duration": 2.0},
        {"action": "land"},
    ]


def test_parse_chinese_move_to_task():
    instruction = "起飞，飞到 x=0.5 y=0.5 z=1.0，悬停 3 秒，然后降落"

    actions = parse_instruction(instruction)

    assert actions == [
        {"action": "takeoff", "altitude": 1.5},
        {"action": "move_to", "position": (0.5, 0.5, 1.0)},
        {"action": "hover", "duration": 3.0},
        {"action": "land"},
    ]


def test_out_of_bounds_move_to_instruction_is_rejected():
    instruction = "take off, move to x=5 y=0 z=1, hover 2 seconds, then land"

    with pytest.raises(ValueError, match="out of bounds"):
        parse_instruction(instruction)


def test_unsupported_chinese_target_color_is_rejected():
    with pytest.raises(ValueError, match="unsupported target color"):
        parse_instruction("起飞，找到青色目标，然后降落")


def test_unsupported_english_target_color_is_rejected():
    with pytest.raises(ValueError, match="unsupported target color"):
        parse_instruction("take off, find the orange target, then land")


def test_unknown_instruction_is_rejected():
    with pytest.raises(ValueError):
        parse_instruction("随便做点什么")


def test_rule_planner_backend_returns_metadata():
    result = plan_instruction("take off, hover 2 seconds, then land")

    assert result.source == "rule"
    assert result.fallback_reason == ""
    assert result.actions == [
        {"action": "takeoff", "altitude": 1.5},
        {"action": "hover", "duration": 2.0},
        {"action": "land"},
    ]


def test_planner_backend_rejects_unsupported_mode():
    with pytest.raises(ValueError, match="Unsupported planner mode"):
        plan_instruction("take off", mode="llm")  # type: ignore[arg-type]
