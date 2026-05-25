# 🧠 Local LLM Agent Deployment Notes
> 在国内网络环境下，从零开始在 Windows 笔记本上部署本地 LLM Agent 的完整实践记录。  
> 包含 Ollama、LiteLLM、Cherry Studio 整合，以及工具调用（Function Calling）的踩坑全记录。
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
---
## 📖 目录
- [背景](#背景)
- [快速开始](#快速开始)
- [架构图](#架构图)
- [项目结构](#项目结构)
- [核心踩坑记录](#核心踩坑记录)
- [技术栈](#技术栈)
- [使用示例](#使用示例)
- [贡献](#贡献)
- [许可证](#许可证)
---
## 背景
**问题**：国内用户在 Windows 环境下部署本地大模型时，会遇到模型下载缓慢、工具调用协议不兼容、客户端 Agent 模式失效等一系列问题。现有教程大多仅停留在 `ollama pull` 成功一步，缺乏对真实故障的完整记录。
**本项目**：记录了我在 **RTX 5060 Laptop (8GB)** + **i9-14900HX** 笔记本上，全程使用国内镜像站和代理工具，最终实现本地模型通过 Python Agent 调用外部工具的过程。所有失败与解决方案均被保留，供后来者参考。
---
## 快速开始
### 环境要求
- Windows 10/11
- Python 3.10+
- [Ollama](https://ollama.com/download) 已安装
- NVIDIA GPU（可选，纯 CPU 也可运行）
1. 安装依赖
```bash
pip install -r requirements.txt
2. 拉取模型
Bash
ollama pull qwen2.5-coder:7b
3. 启动 LiteLLM 代理
Bash
litellm --model ollama/qwen2.5-coder:7b --port 4000
4. 运行 Agent
Bash
python agent.py
在终端输入问题，Agent 将自动调用天气查询、Wikipedia 搜索等工具。

项目结构
Text
local-llm-agent-deployment-notes/
├── README.md              # 项目首页
├── LICENSE                # MIT 协议
├── requirements.txt       # Python 依赖
├── agent.py               # 命令行 Agent 示例
├── Modelfile_*            # Ollama 模型配置示例
└── .gitignore             # Git 忽略规则
核心踩坑记录
1. 模型下载：hf-mirror 限速与多线程策略
单线程 aria2c -x 1 避免触发镜像站限速，稳定在 300 KB/s
hf download 自带校验，适合断点续传
ollama pull 官方库有时可直接访问，速度快于手动下载
2. Abliterated（去审查）模型不可用
bartowski/...-abliterated 版本缺失 chat_template，导致对话乱码、工具调用输出字符串而非 JSON
结论：7B 规模上，去审查技术牺牲了指令遵循能力，得不偿失
3. Ollama 与 OpenAI 函数调用协议差异
Cherry Studio 直接连接 Ollama 时，/v1/chat/completions 端点返回的 tool_calls 格式与 OpenAI 规范有差异
解决方案：引入 LiteLLM 代理，将 Ollama 包装为完全兼容的 OpenAI API
4. Cherry Studio Agent 执行器 Bug
模型已正确返回 tool_calls，但 Cherry Studio 内嵌的 MCP 工具执行器不执行任何 HTTP 请求
临时方案：改用 Python 脚本直接管理工具调用循环，绕过 GUI 限制
5. Modelfile 中的 TEMPLATE 与 stop 冲突
同时指定 TEMPLATE 和 PARAMETER stop 会导致 /v1 端点过滤掉控制 token，返回空消息
解决：只需在 Modelfile 中提供 TEMPLATE，Ollama 会自动推断停止词
技术栈
层级	    技术	                  说明
模型	    Qwen2.5-Coder 7B	       本地推理引擎
模型服务	 Ollama	                   本地模型管理 & API 服务
代理	    LiteLLM	                   OpenAI 协议转换
客户端	    Cherry Studio (部分可用)	GUI 对话客户端
Agent	    agent.py (Python)	           自建工具调用循环
工具	    Open-Meteo API, Wikipedia	通过 HTTP 调用
使用示例
查询天气
Text
You: 查一下北京今天的天气
[调用工具: get_weather] 参数: {'latitude': 34.76, 'longitude': 113.58}
AI: 北京当前温度 21.8°C，风速 17.3 km/h
搜索 Wikipedia
Text
You: 用 Wikipedia 搜索 Qwen 模型
[调用工具: mcp_openinternet] 参数: {'tool_name': 'wikipediaSearch', 'arguments': {'q': 'Qwen'}}
AI: Qwen 是阿里巴巴推出的通用语言模型系列...
贡献
欢迎提 Issue 分享你在本地 Agent 部署中遇到的新坑与解决方案！

许可证
MIT ©yan 



