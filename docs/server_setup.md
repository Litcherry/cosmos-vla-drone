# Remote Server Setup Plan

## Purpose

This document describes the planned remote GPU server setup for running Isaac Sim, Isaac Lab, and later Cosmos-related experiments.

The local laptop is used for:

- Python development
- GitHub workflow
- baseline testing
- mock environment validation
- documentation

The remote server will be used for:

- Isaac Sim simulation
- Isaac Lab reinforcement learning experiments
- high-fidelity rendering
- RGB/depth camera simulation
- future Cosmos model inference or data generation

## Why a Remote Server Is Needed

The local machine has an RTX 3050 Ti Laptop GPU with 4 GB VRAM. This is enough for code development but not enough for full Isaac Sim, Isaac Lab training, or Cosmos model inference.

Isaac Sim requires a strong RTX-class GPU, enough VRAM, enough RAM, and a Linux environment for the container workflow.

## Recommended Server

### Entry-Level Option

- OS: Ubuntu 22.04
- GPU: RTX 4090 24 GB
- RAM: 64 GB
- Storage: 500 GB SSD or larger
- Use case: Isaac Sim smoke tests, simple scenes, small-scale experiments

### Preferred Option

- OS: Ubuntu 22.04
- GPU: L40S 48 GB or RTX 6000 Ada 48 GB
- RAM: 128 GB
- Storage: 1 TB SSD or larger
- Use case: Isaac Sim, Isaac Lab, larger scenes, RGB/depth generation, future Cosmos experiments

## GPUs To Avoid For Isaac Sim Rendering

A100 and H100 are strong training GPUs, but they are not ideal for Isaac Sim graphics workflows because Isaac Sim rendering benefits from RTX GPUs with RT Cores.

If the task is only large model training, A100/H100 may be useful. For Isaac Sim simulation and rendering, RTX 4090, L40S, or RTX 6000 Ada are better choices.

## Initial Server Software

The server should start with:

- Ubuntu 22.04
- NVIDIA driver compatible with CUDA 12.x
- Git
- Python 3.10
- Python virtual environment support
- VS Code Remote SSH access
- Isaac Sim
- Isaac Lab, installed after Isaac Sim works

## Initial Validation Steps

After renting the server, the first checks should be:

```bash
nvidia-smi
```

Expected result:

- NVIDIA GPU is visible
- Driver version is shown
- GPU memory is shown

Then install basic tools:

```
sudo apt update
sudo apt install -y git curl wget build-essential python3 python3-venv python3-pip unzip
```

Then clone this project:

```
mkdir -p ~/projects
cd ~/projects
git clone git@github.com:Litcherry/cosmos-vla-drone.git
cd cosmos-vla-drone
```

Create a Python environment:

```
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
pip install -r requirements-dev.txt
pytest -q
ruff check src tests
```

## Isaac Sim Installation Plan

The first Isaac Sim goal is not to run the full drone project. The first goal is only to confirm Isaac Sim can launch.

Planned steps:

1. Install Isaac Sim following the official workstation or container installation guide.
2. Launch Isaac Sim successfully.
3. Run a minimal empty scene.
4. Run a simple Python script that creates a ground plane.
5. Add a cube as a target object.
6. Add camera output.
7. Connect the project `SceneConfig` and `SceneBuilder` abstractions.

## Isaac Lab Plan

Isaac Lab should be installed only after Isaac Sim is confirmed working.

Isaac Lab will later be used for:

- reinforcement learning environment definition
- parallel simulation
- policy training
- reward design
- post-training experiments

## Development Workflow

The recommended workflow is:

1. Develop and test normal Python code locally in WSL.
2. Push stable code to GitHub.
3. Pull the code on the remote server.
4. Run Isaac Sim and Isaac Lab experiments on the server.
5. Save large outputs outside Git.
6. Commit only source code, configuration, documentation, and small test files.

## Large Files Policy

Do not commit:

- model weights
- Isaac Sim cache files
- large datasets
- generated videos
- training checkpoints
- experiment logs
- synthetic image datasets

These files should be stored outside GitHub or in a separate artifact storage system.

## References

- [Isaac Sim Requirements](https://docs.isaacsim.omniverse.nvidia.com/latest/installation/requirements.html)
- [Isaac Sim Workstation Installation](https://docs.isaacsim.omniverse.nvidia.com/latest/installation/install_workstation.html)
- [Isaac Lab Local Installation](https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html)