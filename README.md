# PEP-2-TestCase

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Powered by DeepAgents](https://img.shields.io/badge/Powered%20by-DeepAgents-purple)](https://github.com/deepagents)

**[English](#english) | [中文](#chinese)**

---

<a name="english"></a>
## 🇬🇧 English

### Introduction

**PEP-2-TestCase** is an intelligent agent system designed to automate the software testing lifecycle for Python Enhancement Proposals (PEPs). It transforms a raw PEP URL into a comprehensive, structured test plan.

Instead of a simple "prompt-to-text" generation, this project implements a **Deep Research Iteration Workflow**. It mimics how a human QA engineer works: first deeply understanding the requirements, and then iteratively designing test cases.

### Core Philosophy: Iteration Research

The workflow is orchestrated using **LangGraph** and split into two distinct phases, each powered by specialized agents:

1.  **Phase 1: Requirement Analysis (The Researcher)**
    *   **Goal**: Build a `PepKnowledgeGraph`.
    *   **Behavior**: The agent reads the PEP, identifies key functional modules, and recursively researches references or ambiguous concepts (using internet search or fetching other PEPs) until it fully understands the specifications.
    *   **Output**: A structured knowledge graph mapping modules to specific requirement atoms.

2.  **Phase 2: Test Case Generation (The Tester)**
    *   **Goal**: Design a `TestPlan`.
    *   **Behavior**: Based on the Knowledge Graph from Phase 1, this agent designs test cases covering positive paths, edge cases, and error conditions. It ensures every requirement is covered.
    *   **Output**: A list of structured test cases (JSON & Markdown).

### Architecture

This project leverages modern Agentic AI frameworks:

*   **[LangGraph](https://github.com/langchain-ai/langgraph)**: Manages the stateful workflow and transitions between the Researcher and Tester phases.
*   **[DeepAgents](https://github.com/deepagents/deepagents)**: Simplifies the construction of complex multi-agent systems (Lead Agent + Sub-Agents). It handles tool routing, loop detection, and recursive reasoning effortlessly.
*   **Rich**: Provides a beautiful, real-time Terminal UI (TUI) to visualize the agent's thought process and execution plan.

### Installation

We recommend using `uv` for modern Python dependency management.

1.  **Clone the repository**
    ```bash
    git clone https://github.com/markshao/pep_2_testcase.git
    cd pep_2_testcase
    ```

2.  **Install dependencies**
    ```bash
    # Install uv if you haven't
    pip install uv

    # Sync dependencies
    uv sync
    ```

3.  **Configure Environment**
    Copy the example environment file and fill in your API keys.
    ```bash
    cp .env.example .env
    ```
    *   `OPENAI_API_KEY`: For the LLM (compatible with OpenAI, Moonshot, DeepSeek, etc.).
    *   `OPENAI_BASE_URL`: Optional, for custom endpoints.
    *   `TAVILY_API_KEY`: For internet search capabilities (required for Deep Research).

### Usage

Run the tool directly with a PEP URL:

```bash
uv run pep2testcase https://peps.python.org/pep-0008/
```

**Artifacts**:
After execution, results are saved in the `artifacts/` directory:
*   `knowledge_graph.json`: The structured requirements.
*   `test_plan.json`: The machine-readable test cases.
*   `test_plan.md`: A human-readable test report.

---

<a name="chinese"></a>
## 🇨🇳 中文

### 项目背景

**PEP-2-TestCase** 是一个智能 Agent 系统，旨在自动化 Python 增强提案 (PEP) 的测试用例设计过程。它能够将一个 PEP URL 直接转化为一份覆盖全面的结构化测试计划。

本项目不只是简单的“文本生成”，而是实现了一种 **深度研究迭代工作流 (Deep Research Iteration Workflow)**。它模拟了人类 QA 工程师的工作方式：先深入理解需求，再迭代设计用例。

### 核心原理：迭代研究 (Iteration Research)

整个工作流通过 **LangGraph** 串联，分为两个核心阶段，每个阶段由专门的 Agent 负责：

1.  **阶段一：需求分析 (Requirement Analysis)**
    *   **角色**: 需求分析 Agent (Researcher)
    *   **目标**: 构建 `PepKnowledgeGraph` (PEP 知识图谱)。
    *   **行为**: Agent 读取 PEP 原文，识别核心功能模块。遇到不清楚的概念或引用的其他 PEP 时，它会主动发起“深度研究”子任务（上网搜索或抓取相关文档），直到完全理解需求。
    *   **产出**: 包含模块划分和具体需求点的结构化知识图谱。

2.  **阶段二：用例生成 (Test Case Generation)**
    *   **角色**: 测试设计 Agent (Tester)
    *   **目标**: 生成 `TestPlan` (测试计划)。
    *   **行为**: 基于阶段一产出的知识图谱，设计覆盖正常路径、边界条件和异常场景的测试用例，确保每个需求点都被覆盖。
    *   **产出**: 结构化的测试用例列表 (JSON 和 Markdown 格式)。

### 技术架构

本项目采用了前沿的 Agentic AI 技术栈：

*   **[LangGraph](https://github.com/langchain-ai/langgraph)**: 负责编排整个状态机工作流，管理从 Researcher 到 Tester 的状态流转。
*   **[DeepAgents](https://github.com/deepagents/deepagents)**: 用于构建复杂的 Multi-Agent 架构。它极大地简化了 Lead Agent（主导者）与 Sub-Agents（子任务执行者）的开发，自动处理工具调用、循环检测和递归推理。
*   **Rich**: 提供了美观的终端交互界面 (TUI)，实时展示 Agent 的思考过程、Plan 执行情况和工具调用日志。

### 安装与使用

推荐使用 `uv` 进行依赖管理。

1.  **克隆代码库**
    ```bash
    git clone https://github.com/markshao/pep_2_testcase.git
    cd pep_2_testcase
    ```

2.  **安装依赖**
    ```bash
    # 如果未安装 uv
    pip install uv

    # 同步依赖
    uv sync
    ```

3.  **配置环境变量**
    复制示例配置并填入 API Key。
    ```bash
    cp .env.example .env
    ```
    *   `OPENAI_API_KEY`: LLM 密钥 (支持 OpenAI, Moonshot, DeepSeek 等)。
    *   `OPENAI_BASE_URL`: 可选，用于自定义模型端点。
    *   `TAVILY_API_KEY`: 用于联网搜索能力 (Deep Research 必须)。

### 使用方法

直接运行命令并指定 PEP URL：

```bash
uv run pep2testcase https://peps.python.org/pep-0008/
```

**输出产物**:
运行完成后，结果将保存在 `artifacts/` 目录下：
*   `knowledge_graph.json`: 结构化的需求知识图谱。
*   `test_plan.json`: 机器可读的测试用例数据。
*   `test_plan.md`: 人类可读的 Markdown 测试报告。
