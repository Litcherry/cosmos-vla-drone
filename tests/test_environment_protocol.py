from cosmos_vla_drone.isaac_env.interfaces import DroneEnvironment
from cosmos_vla_drone.isaac_env.mock_env import MockDroneEnvironment


def test_mock_environment_matches_drone_environment_protocol():
    env = MockDroneEnvironment()

    assert isinstance(env, DroneEnvironment)