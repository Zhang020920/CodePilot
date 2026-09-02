# CodePilot

CodePilot 是一个面向软件开发场景的终端 AI 编程助手，支持在本地项目中完成代码分析、文件修改、命令执行、问题修复、上下文管理和多工具协同。项目基于 Python 构建，提供统一的 LLM 接入、MCP 工具生态扩展、安全权限控制、工作树隔离以及可选的远程 WebSocket 交互模式，适合日常开发和自动化编程任务。

## 项目简介

CodePilot 的目标是把“对话式编程”变成可落地的工程化能力。它不仅能理解用户任务，还能主动读取代码、调用工具、执行命令、修改文件并持续推进任务，形成一个完整的终端智能开发工作流。

项目支持：

- 统一接入不同 LLM 提供商，兼容 `anthropic` 和 `openai` 协议
- 通过 MCP Server 扩展外部工具能力
- 在权限控制下安全执行文件与命令操作
- 支持长会话上下文管理、任务跟踪与多 Agent 协作
- 支持本地终端模式与远程浏览器交互模式

## 项目亮点

### 1. 多模型统一接入

通过 `.codepilot/config.yaml` 配置不同的 LLM 提供商，统一由同一套 Agent 逻辑调度。支持配置 `base_url`、`api_key`、`model` 和 `thinking`，方便切换不同厂商和不同模型。

### 2. MCP 工具扩展能力

项目内置 MCP Server 配置入口，可以通过 `npx` 启动如 `context7` 这类工具服务，也支持后续接入更多 stdio 或 HTTP 类型的 MCP Server，扩展检索、知识查询和自动化能力。

### 3. 安全执行与权限控制

CodePilot 在执行命令和修改文件前会结合权限模式、危险命令检测、路径沙箱和规则引擎进行校验，降低 AI 自动操作本地环境的风险。

### 4. 面向真实开发流程设计

项目将 Agent、工具注册、会话上下文、工作树隔离、任务管理与协作机制拆分为独立模块，更贴近真实的软件工程任务，而不是单轮问答式助手。

### 5. 支持远程交互

除了本地 CLI 模式外，还支持 `--remote` 启动 WebSocket 服务，适合通过浏览器界面连接和操作。

## 技术栈

- Python 3.11+
- uv
- Textual
- Anthropic API
- OpenAI SDK
- MCP
- PyYAML
- Pydantic
- httpx
- websockets
- ReAct Agent
- Multi-Agent
- Git Worktree

## 核心流程

1. 用户通过 CLI、非交互模式或远程模式发起任务。
2. 程序加载 `.codepilot/config.yaml`，初始化 LLM 提供商、MCP Server、权限模式、沙箱和工作树配置。
3. Agent 根据系统提示词和当前任务构建上下文，并从工具注册中心获取可用能力。
4. 当模型需要执行操作时，Agent 进行工具调用，包括文件读取、命令执行、任务管理、团队协作或外部 MCP 工具调用。
5. 权限系统对敏感操作进行检测和拦截，必要时触发人工确认。
6. 执行结果回流到会话上下文，继续驱动后续推理，直到任务完成。

## 配置说明

在项目根目录下编辑 `.codepilot/config.yaml`，填入你的 LLM 和 MCP 配置。

```yaml
providers:
  - name: anthropic-official
    protocol: anthropic
    base_url: https://your-api-provider.com/api/anthropic
    api_key: "your-api-key-here"
    model: claude-sonnet-4-6
    thinking: true

mcp_servers:
  - name: context7
    command: npx
    args: ["-y", "@upstash/context7-mcp"]
```

### 配置说明

- `protocol`：填写 `anthropic` 或 `openai`，取决于你的提供商兼容哪种 API
- `base_url`：你的 API 地址
- `api_key`：你的 API Key
- `model`：模型名称
- `thinking`：是否开启 extended thinking
- `mcp_servers`：MCP Server 列表，每项需要 `name`、`command` 和 `args`

### 注意事项

- 如果 MCP Server 配置报错，可以先安装 Node.js，因为启动 MCP Server 需要 `npx`
- 推荐将真实密钥保存在本地配置文件中，不要提交到公开仓库

## 安装与运行

环境要求：Python 3.11+、[uv](https://docs.astral.sh/uv/)

```bash
# 安装依赖
uv sync

# 运行
uv run CodePilot

# 测试
uv run pytest
```

## 常用启动方式

```bash
# 指定权限模式启动
uv run CodePilot --mode default

# 非交互模式执行一个 prompt
uv run CodePilot -p "帮我分析这个项目的入口"

# 以 stream-json 输出结果
uv run CodePilot -p "总结仓库结构" --output-format stream-json

# 启动远程模式
uv run CodePilot --remote
```

## 项目结构

```text
.
├── .codepilot/                # 本地配置目录
│   ├── config.yaml.example  # 配置示例
│   └── ...
├── codepilot/                 # 核心源码包
│   ├── __main__.py          # 命令行入口
│   ├── agent.py             # Agent 主流程
│   ├── app.py               # 本地 UI / 应用入口
│   ├── client.py            # LLM 客户端封装
│   ├── config.py            # 配置加载与校验
│   ├── conversation.py      # 会话管理
│   ├── driver.py            # 运行驱动
│   ├── mcp/                 # MCP 相关能力
│   ├── permissions/         # 权限与安全控制
│   ├── sandbox/             # 沙箱执行支持
│   ├── tools/               # 内置工具注册与实现
│   ├── teams/               # 多 Agent 协作
│   ├── worktree/            # Git Worktree 管理
│   └── ...
├── tests/                   # 测试代码
├── pyproject.toml           # 项目与依赖配置
├── uv.lock                  # 锁定文件

```

## 适合场景

- 代码仓库问答与结构分析
- 自动修复报错和重构代码
- 辅助执行测试、构建和命令行任务
- 需要工具调用和多轮上下文的开发场景
- 需要安全权限控制的本地 AI 编程助手场景


