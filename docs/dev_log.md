# 开发日志

## 2026-07-06

### 今日目标

- 从空 GitHub 仓库开始搭建 Cosmos VLA Drone 项目。
- 明确本地电脑、WSL2 和远程 GPU 服务器的分工。
- 建立项目初始目录结构。
- 准备后续迁移 baseline、接入 Isaac Sim 和 Cosmos 的工程基础。

### 已完成

- 创建并克隆空 GitHub 仓库。
- 添加 README、`.gitignore` 和基础说明文件。
- 建立 Python 项目骨架，包括 `src/cosmos_vla_drone` 和 `tests`。
- 建立核心模块目录：`baseline`、`isaac_env`、`cosmos_bridge`、`memory`、`policy`、`evaluation`。
- 编写环境配置说明，记录本地电脑不适合作为主要 Isaac Sim / Cosmos 运行环境。

### 环境判断

本地电脑使用 Windows 11 和 RTX 3050 Ti Laptop GPU，显存为 4 GB。该配置适合本地开发、文档维护、GitHub 工作流和轻量测试，但不适合完整运行 Isaac Sim、Isaac Lab 强化学习训练或 Cosmos 模型推理。

后续计划采用以下方式：

- 本地 Windows：代码开发和文档维护。
- WSL2 Ubuntu：普通 Linux 开发和测试。
- 远程 Linux GPU 服务器：Isaac Sim、Isaac Lab 和 Cosmos 实验。

### 下一步

- 完成 Python 本地开发环境。
- 确认 WSL2 Ubuntu 是否安装。
- 规划远程 GPU 服务器规格。
- 迁移旧 VLA 无人机项目中的 planner 和 action schema 作为 baseline。
