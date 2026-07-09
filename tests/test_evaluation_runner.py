from cosmos_vla_drone.evaluation.runner import run_task_in_environment
from cosmos_vla_drone.isaac_env.mock_env import MockDroneEnvironment


def test_run_task_in_mock_environment_successfully():
    env = MockDroneEnvironment()
    result = run_task_in_environment(
        "起飞，找到红色目标，飞到它上方 1 米处悬停 5 秒，然后降落",
        env,
    )

    assert result.success is True
    assert result.failure_reason == ""
    assert result.planner_source == "rule"
    assert result.environment_result.final_observation.position == (1.5, 0.8, 0.0)
    assert [event.action for event in result.environment_result.events] == [
        "takeoff",
        "search",
        "move_above",
        "hover",
        "land",
    ]


def test_run_task_in_mock_environment_reports_failure():
    env = MockDroneEnvironment(targets={})
    result = run_task_in_environment(
        "起飞，找到红色目标，飞到它上方 1 米处悬停 5 秒，然后降落",
        env,
    )

    assert result.success is False
    assert "target not found: red" in result.failure_reason