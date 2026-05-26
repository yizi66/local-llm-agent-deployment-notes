Markdown
# 各组件版本记录
本文件记录了本次本地 LLM Agent 部署过程中使用的所有软件及模型版本。  
部分版本号为事后补充查询，标注 [已确认] 表示从日志或输出中直接提取，标注 [待补充] 表示需在实际环境中重新查询。
---
## 模型
| 组件 | 版本 / 标识 | 来源 |
|------|------------|------|
| Qwen2.5-Coder 7B | `qwen2.5-coder:7b` (Ollama 官方库) | `ollama pull qwen2.5-coder:7b` |
| 量化格式 | Q4_K_M | 自动选择 |
---
## 模型服务
| 组件 | 版本 | 确认方式 |
|------|------|----------|
| Ollama | **0.24.0** | 日志 `msg="Listening on 127.0.0.1:11434 (version 0.24.0)"` |
---
## 代理层
| 组件 | 版本 | 安装命令 |
|------|------|----------|
| LiteLLM | [待补充] | `pip install 'litellm[proxy]'` |
查询方式：
```powershell
pip show litellm | findstr Version
Python 环境
组件	        版本	         查询命令
Python	       3.13.9         python --version
huggingface_hub	1.16.1	    `pip show huggingface_hub
requests	    2.32.5  	    `pip show requests
下载工具
组件	版本	确认方式
aria2	1.37.0	aria2c --version
客户端
组件	版本	确认方式
Cherry Studio	v1.96	设置 → 关于
GPU 驱动与 CUDA
组件	            版本	            确认方式
NVIDIA 驱动 	  12.8	               日志 driver=12.8
CUDA compute	   12.0              	日志 compute=12.0
GPU	NVIDIA GeForce RTX 5060 Laptop GPU	日志 name="NVIDIA GeForce RTX 5060 Laptop GPU"
显存	8.0 GiB	日志 total="8.0 GiB"
Git
组件	           版本          	查询命令
Git for Windows	2.54.0.windows.1	git --version
备注
Ollama 日志路径：%LOCALAPPDATA%\Ollama\server.log
以上补充 版本 项可由读者（包括未来的自己）在各自环境中通过对应查询命令获取
本次部署网络环境：中国大陆，使用 hf-mirror.com 及其他镜像站
