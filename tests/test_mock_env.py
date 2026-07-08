from cosmos_vla_drone.baseline.runner import run_baseline_task
from cosmos_vla_drone.isaac_env.mock_env import MockDroneEnvironment


def test_mock_env_executes_baseline_plan():
    task = "起飞，找到红色目标，飞到它上方 1 米处悬停 5 秒，然后降落"
    plan = run_baseline_task(task)

    env = MockDroneEnvironment()
    result = env.execute_plan(plan.actions)

    assert result.success is True
    assert result.final_position == (1.5, 0.8, 0.0)
    assert [event["action"] for event in result.events] == [
        "takeoff",
        "search",
        "move_above",
        "hover",
        "land",
    ]


def test_mock_env_reports_missing_target_failure():
    actions = [
        {"action": "takeoff", "altitude": 1.5},
        {"action": "search", "target": "red"},
    ]

    env = MockDroneEnvironment(targets={})
    result = env.execute_plan(actions)

    assert result.success is False
    assert "target not found: red" in result.failure_reason


def test_mock_env_can_reset_state():
    env = MockDroneEnvironment()
    env.execute_plan([{"action": "takeoff", "altitude": 1.5}])

    state = env.reset()

    assert tuple(state.position) == (0.0, 0.0, 0.0)
    assert state.airborne is False
    assert state.last_target is None