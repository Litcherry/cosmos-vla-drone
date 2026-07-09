from cosmos_vla_drone.isaac_env.interfaces import (
    DroneObservation,
    EnvironmentEvent,
    EnvironmentResult,
)


def test_environment_result_structures_are_available():
    observation = DroneObservation(position=(0.0, 0.0, 0.0), airborne=False)
    event = EnvironmentEvent(action="reset", position=(0.0, 0.0, 0.0), airborne=False)
    result = EnvironmentResult(success=True, final_observation=observation, events=[event])

    assert result.success is True
    assert result.final_observation.position == (0.0, 0.0, 0.0)
    assert result.events[0].action == "reset"