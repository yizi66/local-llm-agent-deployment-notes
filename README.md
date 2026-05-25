\# 本地 LLM Agent 部署踩坑记录

\## 硬件基线

\- GPU: NVIDIA RTX 5060 Laptop 8GB (50W TGP)

\- CPU: Intel i9-14900HX

\- RAM: 16GB

\- OS: Windows

\## 部署链

1\. Ollama 安装 + 模型下载（含 hf-mirror 镜像使用）

2\. LiteLLM 代理配置（解决 Ollama function calling 与 OpenAI 格式不兼容）

3\. Cherry Studio Agent 模式已知 bug 及绕过方案

4\. Python 命令行 Agent 原型（天气查询 + MCP 工具总线）

\## 关键坑点

\- abliterated 模型导致对话乱码

\- Cherry Studio Agent 对 Ollama 的 tool\_calls 不执行

\- hf-mirror 限速及多镜像测试结果

\- ollama create 命名冲突

\## 文件说明

\- agent.py: 命令行 Agent 原型

\- Modelfile\_\*: 模型导入配置示例

\- 技术全览.md: 完整命令速查

\## 许可

MIT

