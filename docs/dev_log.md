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
