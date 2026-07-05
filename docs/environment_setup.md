# 环境配置说明

## 总体思路

本项目会同时涉及普通 Python 开发、Isaac Sim 仿真、Isaac Lab 强化学习环境，以及 NVIDIA Cosmos 模型接口。由于 Isaac Sim 和 Cosmos 对显卡、显存和系统环境要求较高，本项目采用分层开发方式：

- 本地 Windows 电脑：用于写代码、写文档、GitHub 提交、轻量测试和 baseline 开发。
- WSL2 Ubuntu：用于熟悉 Linux 开发环境、运行普通 Python 测试、保持和服务器环境接近。
- 远程 Linux GPU 服务器：用于运行 Isaac Sim、Isaac Lab、Cosmos 推理或后训练实验。

## 本地开发电脑

当前本地电脑配置：

- 操作系统：Windows 11
- CPU：12th Gen Intel(R) Core(TM) i5-12500H
- GPU：NVIDIA GeForce RTX 3050 Ti Laptop GPU
- 显存：4 GB

本地电脑适合承担以下任务：

- 项目代码开发
- Git 和 GitHub 工作流
- 文档和实验日志维护
- baseline 模块开发
- 单元测试
- mock 仿真环境开发

本地电脑不适合作为主要 Isaac Sim / Cosmos 运行环境，原因是显存较小，难以支撑高保真仿真、并行强化学习训练或大型世界模型推理。

## WSL2 Ubuntu 环境

WSL2 Ubuntu 主要用于构建接近 Linux 服务器的开发体验。建议安装 Ubuntu 22.04。

WSL2 适合：

- 运行普通 Python 脚本
- 运行单元测试
- 熟悉 Linux 命令行
- 通过 SSH 连接远程 GPU 服务器

WSL2 暂不作为主要 Isaac Sim 运行环境。Isaac Sim 涉及图形渲染、传感器仿真和 GPU 加速，直接在远程 Linux GPU 服务器上运行会更加稳定。

## 远程 GPU 服务器计划

完整 Isaac Sim 仿真、Isaac Lab 强化学习训练和 Cosmos 模型推理计划放在远程 Linux GPU 服务器上运行。

推荐服务器配置：

- 操作系统：Ubuntu 22.04
- GPU：RTX 4090 24 GB 起步
- 更推荐 GPU：L40S 48 GB 或 RTX 6000 Ada 48 GB
- 内存：至少 64 GB，推荐 128 GB
- 硬盘：至少 500 GB SSD，推荐 1 TB
- 驱动：支持 CUDA 12.x 的 NVIDIA 驱动

短期阶段可以先使用 RTX 4090 24 GB 服务器，主要用于 Isaac Sim 小场景和轻量实验。后续如果需要运行 Cosmos Nano、视频推理、合成数据生成或更大规模训练，再升级到 48 GB 显存服务器。

## Isaac Sim

Isaac Sim 是 NVIDIA 的高保真机器人仿真平台，用于构建无人机飞行环境、障碍物、目标物体、相机和物理交互。

本项目中 Isaac Sim 的作用：

- 构建比 PyBullet 更复杂的无人机仿真环境
- 提供相机、深度、位姿等传感器观测
- 生成探索轨迹和实验数据
- 为后续 Isaac Lab 强化学习实验提供仿真基础

## Isaac Lab

Isaac Lab 是基于 Isaac Sim 的机器人学习框架，适合做强化学习、并行仿真和 policy 训练。

本项目中 Isaac Lab 的作用：

- 封装无人机探索任务
- 定义 observation、action、reward 和 termination
- 支持 policy learning 或 post-training 实验

Isaac Lab 不在项目第一天安装，等 Isaac Sim 环境确认可用后再配置。

## NVIDIA Cosmos

Cosmos 是 NVIDIA 面向 Physical AI 的世界模型生态，不是一个普通的小型 Python 库。它可以用于世界理解、未来预测、动作推理、视频生成和合成数据生成。

本项目中 Cosmos 的预期作用：

- 辅助无人机理解当前场景
- 对候选动作进行物理合理性判断
- 根据观测预测未来状态
- 生成或增强 synthetic data
- 作为 policy learning 的辅助模块

由于 Cosmos 模型较大，本地电脑不直接运行 Cosmos。项目早期会先实现 `cosmos_bridge` 接口和 mock client，等远程 GPU 环境准备好后再接入真实模型或服务。

## 开发原则

- 模型权重、仿真缓存、视频输出和训练 checkpoint 不提交到 GitHub。
- 本地仓库只保存代码、配置、文档、小型测试数据和实验说明。
- 每个开发日更新开发日志。
- 每个阶段保留清晰的 commit 历史和 pull request 记录。
