# 开发日志

## 2026-07-06

### 今日目标

- [x] 从空 GitHub 仓库开始搭建 Cosmos VLA Drone 项目。
- [x] 明确本地电脑、WSL2 和远程 GPU 服务器的分工。
- [x] 建立项目初始目录结构。
- [x] 准备后续迁移 baseline、接入 Isaac Sim 和 Cosmos 的工程基础。

### 完成情况

- 创建并克隆空 GitHub 仓库。
- 添加 README、`.gitignore` 和基础说明文件。
- 建立 Python 项目骨架，包括 `src/cosmos_vla_drone` 和 `tests`。
- 建立核心模块目录：`baseline`、`isaac_env`、`cosmos_bridge`、`memory`、`policy`、`evaluation`。
- 编写环境配置说明，记录本地电脑不适合作为主要 Isaac Sim / Cosmos 运行环境。

## 2026-07-08

### 今日目标

- [x] 将项目迁移到 WSL Linux 原生目录中开发。
- [x] 迁移旧 VLA Drone 项目的 baseline 规划能力。
- [x] 建立阶段一最小闭环：自然语言指令 -> 动作计划 -> mock 执行结果。
- [x] 为后续 Isaac Sim 环境接入打基础。

### 完成情况

- 将项目 clone 到 `~/projects/cosmos-vla-drone`，避免长期在 `/mnt/c` Windows 挂载目录中开发。
- 重新配置 Python 虚拟环境，并确认 VS Code / WSL 使用 `.venv` 中的解释器。
- 清理 `requirements-dev.txt`，将其简化为开发依赖文件，只保留 `pytest` 和 `ruff`。
- 迁移并整理 baseline 模块，包括 action schema、rule planner、planner backend 和 safety check。
- 新增 baseline runner，用于把自然语言任务转换为结构化动作计划。
- 新增 mock drone environment，在不依赖 Isaac Sim / PyBullet 的情况下模拟动作执行。
- 添加并通过 planner、schema、safety、runner 和 mock environment 的单元测试，测试结果全部通过。

### 遇到的问题

- 最开始项目目录建立在windows目录下，考虑到环境、兼容性、写入速度等因素，认为不适合作为长期 Linux 开发环境，因此迁移到了 WSL 的 `~/projects` 目录。
- 之前使用 `pip freeze` 生成的 `requirements-dev.txt` 包含了当前项目的 Git 安装记录，不适合作为开发依赖文件，后来改成手写的轻量依赖列表。使用 `pyproject.toml` 记录项目依赖。

### 今日收获

- 学习并学会使用 `pyproject.toml` 

### 下一步

- 进入阶段二：设计 Isaac Sim 环境接口。

## 2026-07-09

### 今日目标

- [x] 在远程 RTX 4090 服务器上配置项目运行环境。
- [x] 安装并验证 Isaac Sim Python 环境。
- [x] 运行 Isaac Sim headless smoke test。
- [x] 排查服务器上的 conda、Vulkan 和 Isaac Sim 启动问题。

### 完成情况

- 租用 AutoDL RTX 4090 服务器，配置为 Ubuntu 22.04、RTX 4090 24GB、Python 3.10、CUDA 12.2 driver runtime。
- 将项目 clone 到服务器数据盘 `/root/autodl-tmp/projects/cosmos-vla-drone`。
- 创建项目开发环境 `/root/autodl-tmp/conda-envs/cosmos-vla-drone`，并通过项目测试。
- 创建 Isaac Sim 专用环境 `/root/autodl-tmp/conda-envs/isaacsim`，使用 Python 3.12。
- 成功安装 `isaacsim==6.0.1.0`。
- 成功运行 Isaac Sim headless smoke test：
  - 启动 `SimulationApp`
  - 创建 `World`
  - 添加 default ground plane
  - 执行 simulation step
  - 正常关闭 Isaac Sim
- 将 Isaac Sim smoke test 整理为项目脚本 `scripts/isaac_smoke_test.py`，方便后续服务器复现。

### 遇到的问题

#### 1. Pylance 语法检查报错

Pylance 语法检查报错，接口函数未写函数体报错，函数后加`...`,防止语法报错 

#### 2. 服务器驱动版本过低

当前 NVIDIA driver 版本低于 Isaac Sim RTX 推荐要求：当前租的服务器驱动 **535.129.03 太旧**（saac Sim / Omniverse RTX 官方最低要求 550.90.07

报错信息：

```
R550 Omniverse RTX driver requirement on Linux
Installed driver: 535.129.03
The unsupported driver range: [0.00, 550.90.07)
rtx driver verification failed
```

当前可以做：
- headless SimulationApp smoke test
- World 创建
- ground plane
- 基础 physics / API 探索

后面可能受影响：
- RTX 渲染
- RGB camera
- depth camera
- synthetic data
- 高质量视觉输出

#### 3. conda activate 在远程终端中不可用

远程服务器在新开的终端一开始执行：

```bash
conda activate /root/autodl-tmp/conda-envs/isaacsim
```

会报错：

```bash
CommandNotFoundError: Your shell has not been properly configured to use 'conda activate'.
```

原因是当前 shell 没有加载 conda 的初始化脚本。

临时解决方法：

```bash
source /root/miniconda3/etc/profile.d/conda.sh
conda activate /root/autodl-tmp/conda-envs/isaacsim
```

永久解决方法：

```bash
/root/miniconda3/bin/conda init bash
source ~/.bashrc
```

之后新开的远程终端就可以直接使用 `conda activate`。

#### 2. Isaac Sim 一开始出现 Vulkan / RTX 初始化错误

第一次运行 Isaac Sim 时出现过类似错误：

```bash
VkResult: ERROR_INCOMPATIBLE_DRIVER
vkCreateInstance failed
Failed to create any GPU devices
GPU Foundation is not initialized
```

排查后发现，系统默认的 Vulkan ICD 目录 `/usr/share/vulkan/icd.d` 中没有 NVIDIA ICD，只包含 Intel、Radeon、llvmpipe 等 ICD。Isaac Sim 没有显式使用 NVIDIA Vulkan ICD，导致 RTX/Vulkan 初始化失败。

通过查找 NVIDIA ICD：

```
find / -name "*nvidia*icd*.json" 2>/dev/null
```

找到：

```
/etc/vulkan/icd.d/nvidia_icd.json
```

之后设置：

```
export VK_ICD_FILENAMES=/etc/vulkan/icd.d/nvidia_icd.json
```

再运行：

```
vulkaninfo --summary
```

确认 Vulkan 只使用 NVIDIA RTX 4090。之后 Isaac Sim smoke test 可以正常执行。

### 今日收获

- 明确了项目开发环境和 Isaac Sim 环境需要分开管理：
  - `/root/autodl-tmp/conda-envs/cosmos-vla-drone`：项目开发、测试、普通 Python 代码。
  - `/root/autodl-tmp/conda-envs/isaacsim`：Isaac Sim 运行环境。
- 明确了 Isaac Sim 不只是需要 CUDA 可见，还需要 Vulkan / RTX 渲染栈正确配置。
- 学会了通过 `VK_ICD_FILENAMES` 强制 Vulkan 使用 NVIDIA ICD。
- 完成了服务器端 Isaac Sim 最小 smoke test，为后续真实场景构建打下基础。
