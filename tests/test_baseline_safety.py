import pytest

from cosmos_vla_drone.baseline.safety import (
    assert_plan_safe,
    check_plan_safety,
    is_position_in_bounds,
)


def test_position_inside_workspace_is_allowed():
    assert is_position_in_bounds((0.0, 0.0, 1.0))


def test_position_outside_workspace_is_rejected():
    assert not is_position_in_bounds((4.0, 0.0, 1.0))


def test_safe_plan_has_no_violations():
    actions = [
        {"action": "takeoff", "altitude": 1.5},
        {"action": "move_to", "position": (1.0, 1.0, 1.0)},
        {"action": "land"},
    ]

    assert check_plan_safety(actions) == []


def test_move_to_out_of_bounds_returns_violation():
    actions = [{"action": "move_to", "position": (5.0, 0.0, 1.0)}]

    violations = check_plan_safety(actions)

    assert violations == ["action 0 move_to position out of bounds: (5.0, 0.0, 1.0)"]


def test_assert_plan_safe_raises_for_unsafe_plan():
    actions = [{"action": "move_to", "position": (5.0, 0.0, 1.0)}]

    with pytest.raises(ValueError, match="out of bounds"):
        assert_plan_safe(actions)
