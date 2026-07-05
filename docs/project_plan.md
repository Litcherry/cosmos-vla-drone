# 项目计划

## 项目目标

本项目目标是构建一个基于 NVIDIA Cosmos 和 Isaac Sim 的 VLA 无人机智能体系统。系统将从已有的 PyBullet VLA 无人机项目出发，逐步升级为支持高保真仿真、世界模型辅助推理、记忆系统和策略学习的 embodied AI 研究项目。

## 研究主线

项目围绕以下问题展开：

- 如何让无人机根据自然语言任务进行规划和行动？
- 如何使用 Isaac Sim 构建更复杂、更真实的仿真环境？
- 如何引入 Cosmos 进行场景理解、未来预测或动作合理性判断？
- 如何在探索过程中建立空间记忆、语义记忆和情节记忆？
- 如何基于仿真环境进行 policy learning 或 post-training？

## 项目阶段

### 阶段 1：仓库和环境准备

- 从空 GitHub 仓库开始开发。
- 建立 Python 项目骨架。
- 编写环境配置、项目计划和开发日志。
- 明确本地开发、WSL2 和远程 GPU 服务器的分工。

### 阶段 2：baseline 迁移

- 从旧项目中迁移 planner、action schema 和基础 evaluation 逻辑。
- 保留旧项目作为研究 baseline。
- 添加单元测试，确保基础规划闭环可复现。

### 阶段 3：Isaac Sim 环境

- 构建最小无人机仿真场景。
- 添加目标物体、障碍物和相机观测。
- 设计统一环境接口，为后续强化学习和 Cosmos 接入做准备。

### 阶段 4：Cosmos 接口

- 先实现 mock Cosmos client，避免早期依赖大型模型。
- 后续接入真实 Cosmos Reasoner 或 Generator。
- 探索使用 Cosmos 进行场景理解、未来预测和 synthetic data 生成。

### 阶段 5：记忆系统

- 实现空间记忆，用于记录地图、位置和可达区域。
- 实现语义记忆，用于记录目标物体、场景标签和任务相关信息。
- 实现情节记忆，用于记录探索过程、成功经验和失败事件。

### 阶段 6：策略学习与实验

- 基于 Isaac Lab 或自定义环境进行 policy evaluation。
- 尝试 reinforcement learning 或后训练。
- 设计对比实验，分析 Cosmos 和记忆系统对任务完成率的影响。

## GitHub 开发要求

- 从空仓库开始开发。
- 每个开发日至少 2 个有效 commit。
- 总 commit 数不少于 10。
- commit message 必须具体，不能只写 `update`、`fix`、`final`。
- 至少提交 2 个 pull request，可以自己 merge。
- 每个开发日在 `docs/dev_log.md` 中记录 progress log。

## 当前开发原则

- 不把模型权重、训练 checkpoint、视频输出和大型仿真缓存提交到 GitHub。
- 每次 commit 聚焦一个明确主题。
- 先建立轻量可测试闭环，再逐步接入 Isaac Sim 和 Cosmos。
- 优先保证研究过程清楚、可复现、可解释。
