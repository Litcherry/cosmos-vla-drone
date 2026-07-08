from cosmos_vla_drone.baseline.runner import run_baseline_task, run_baseline_task_as_dict


def test_run_baseline_task_returns_structured_result():
    result = run_baseline_task("起飞，找到红色目标，飞到它上方 1 米处悬停 5 秒，然后降落")

    assert result.instruction
    assert result.planner_source == "rule"
    assert result.planner_fallback_reason == ""
    assert result.actions == [
        {"action": "takeoff", "altitude": 1.5},
        {"action": "search", "target": "red"},
        {"action": "move_above", "target": "red", "height": 1.0},
        {"action": "hover", "duration": 5.0},
        {"action": "land"},
    ]


def test_run_baseline_task_as_dict_is_json_ready():
    result = run_baseline_task_as_dict("take off, hover 2 seconds, then land")

    assert result == {
        "instruction": "take off, hover 2 seconds, then land",
        "actions": [
            {"action": "takeoff", "altitude": 1.5},
            {"action": "hover", "duration": 2.0},
            {"action": "land"},
        ],
        "planner_source": "rule",
        "planner_fallback_reason": "",
    }