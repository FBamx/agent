# Agent 项目说明

本项目是一个基于 LLM（大语言模型）和 MCP 工具集成的智能助手，支持多种工具调用和对话功能。

## 依赖管理

本项目使用 [uv](https://github.com/astral-sh/uv) 作为包管理工具，推荐使用 uv 进行依赖安装和项目运行。

## 快速开始

1. **克隆项目**

```bash
git clone https://github.com/FBamx/agent.git
cd agent
```

2. **安装依赖**

确保已安装 [uv](https://github.com/astral-sh/uv)：

```bash
uv sync
```

3. **启动项目**

```bash
uv run main.py
```

## 目录结构

- `main.py`：主入口，启动 AI 助手。
- `llm.py`：大语言模型客户端与工具调用逻辑。
- `mcp_client.py`：MCP 工具客户端。
- `mcp_server/server.py`：MCP 工具示例服务（如天气查询、GitHub 仓库查询）。
- `chat_assistant/`：包含另一个对话助手实现。
- `pyproject.toml`：依赖与项目配置。

## 主要功能

- 支持通过 LLM 进行多轮对话。
- 可集成 MCP 工具，实现如天气查询等扩展功能。
- 依赖管理简单，使用 uv 一键同步和运行。

## 参考
- [uv 官方文档](https://github.com/astral-sh/uv)
- [项目主页](https://github.com/FBamx/agent)