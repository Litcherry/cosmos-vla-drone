import pytest

from cosmos_vla_drone.baseline.schema import validate_plan


def test_valid_plan_passes_validation():
    raw_actions = [
        {"action": "takeoff", "altitude": 1.5},
        {"action": "search", "target": "red"},
        {"action": "move_above", "target": "red", "height": 1.0},
        {"action": "hover", "duration": 5},
        {"action": "land"},
    ]

    validated = validate_plan(raw_actions)

    assert validated == raw_actions


def test_takeoff_requires_altitude():
    raw_actions = [{"action": "takeoff"}]

    with pytest.raises(ValueError, match="Invalid action plan"):
        validate_plan(raw_actions)


def test_search_requires_target():
    raw_actions = [{"action": "search"}]

    with pytest.raises(ValueError, match="Invalid action plan"):
        validate_plan(raw_actions)


def test_move_above_requires_target_and_height():
    raw_actions = [{"action": "move_above", "target": "red"}]

    with pytest.raises(ValueError, match="Invalid action plan"):
        validate_plan(raw_actions)


def test_rejects_unsupported_target_color():
    raw_actions = [{"action": "search", "target": "yellow"}]

    with pytest.raises(ValueError, match="Invalid action plan"):
        validate_plan(raw_actions)


def test_rejects_unsafe_altitude():
    raw_actions = [{"action": "takeoff", "altitude": 10.0}]

    with pytest.raises(ValueError, match="Invalid action plan"):
        validate_plan(raw_actions)
