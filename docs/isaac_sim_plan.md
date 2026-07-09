# Isaac Sim Integration Plan

## Goal

> vla-drone-agent (PyBullet) → Cosmos-VLA-Drone (Isaac Sim)

The goal of the Isaac Sim stage is to replace the previous simple PyBullet simulation environment with a high-fidelity drone simulation environment. The simulation will support physical interaction, visual perception, obstacle-rich exploration, and future integration with Cosmos-based world understanding.

## Current Baseline

The current project has completed a minimal baseline loop:

```text
Natural language instruction
-> baseline planner
-> action schema validation
-> safety check
-> environment execution
-> structured result and event log
```

The current `MockDroneEnvironment` is intentionally simple. It only verifies the software interface and does not model real physics.

## Why Isaac Sim

Isaac Sim will be used because it supports:

- High-fidelity 3D simulation
- Rigid-body physics
- Collision detection
- RGB and depth cameras
- Sensor simulation
- USD scene construction
- Robot control interfaces
- Integration with Isaac Lab for reinforcement learning

## Target Environment

The first Isaac Sim environment should include:

- A ground plane
- A drone or simplified flying robot body
- Colored target objects
- Walls or maze-like obstacles
  - RGB camera        
- Depth camera
- Drone pose state
- Collision state
- Task success and failure signals

## Environment Interface

The Isaac Sim environment should follow the same interface as the mock environment:

```
reset() -> DroneObservation
execute_plan(actions) -> EnvironmentResult
```

This keeps the planner independent from the simulation backend.

## Planned Observation Fields

The observation should gradually include:

- Drone position
- Drone orientation
- Linear velocity
- Angular velocity
- Airborne state
- RGB frame path or RGB array
- Depth frame path or depth array
- Last detected target
- Collision information
- Semantic scene metadata

## Planned Action Support

The first Isaac Sim version should support the same high-level actions as the baseline:

- `takeoff`
- `search`
- `move_to`
- `move_above`
- `hover`
- `land`

Later versions can add lower-level control:

- velocity commands
- acceleration commands
- attitude commands
- waypoint following
- obstacle avoidance commands

## Physics Features To Add Gradually

The project should not implement all physical details at once. Physics fidelity will be added step by step:

1. Position-based control
2. Velocity limits
3. Acceleration limits
4. Gravity-aware motion
5. Collision detection
6. Control noise
7. Pose and attitude state
8. Drone dynamics model
9. Battery or time budget constraints

## Perception Plan

The first perception system can use simulator ground truth to locate colored targets. Later versions should replace or supplement this with visual perception:

- RGB image target detection
- YOLO-based object detection
- Depth-based target localization
- Open-vocabulary detection
- Semantic mapping

## Cosmos Integration Points

Cosmos should not be treated as a replacement for the simulator. It will be integrated as an intelligence layer around the simulated environment.

Possible integration points:

- Scene understanding from RGB or video observations
- Predicting future outcomes of candidate actions
- Checking whether a planned action is physically plausible
- Generating synthetic training data
- Supporting memory construction during exploration
- Assisting policy learning or post-training

## Server Plan

The local machine is not suitable for full Isaac Sim or Cosmos workloads. The recommended remote machine is:

- OS: Ubuntu 22.04
- GPU: RTX 4090 24 GB as the entry-level option
- Better GPU: L40S 48 GB or RTX 6000 Ada 48 GB
- RAM: 64 GB minimum, 128 GB preferred
- Storage: 500 GB minimum, 1 TB preferred

The project should first complete local interface design and mock environment validation before renting a server.

## Milestones

### Milestone 1: Interface Alignment

- Define shared environment interfaces.
- Make `MockDroneEnvironment` implement the same result structure expected from Isaac Sim.
- Keep planner independent from the environment backend.

### Milestone 2: Isaac Sim Smoke Test

- Install Isaac Sim on a remote Linux GPU server.
- Launch Isaac Sim successfully.
- Run a minimal Python script that opens an empty scene.

### Milestone 3: Minimal Drone Scene

- Add ground plane.
- Add target objects.
- Add a simplified drone body.
- Read drone position.
- Move the drone with position commands.

### Milestone 4: Visual Observation

- Add RGB camera.
- Add depth camera.
- Save sample frames.
- Connect observations to the project interface.

### Milestone 5: Obstacle Exploration

- Add walls or maze-like obstacles.
- Add collision detection.
- Execute simple search tasks.

### Milestone 6: Cosmos-Ready Data

- Save observations, actions, events, and trajectories.
- Prepare data format for Cosmos-based reasoning or synthetic data experiments.