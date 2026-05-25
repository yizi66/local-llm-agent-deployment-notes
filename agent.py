import requests
import json
# --- 配置 ---
LITELLM_URL = "http://localhost:4000/v1/chat/completions"
MODEL_NAME = "qwen2.5-coder:7b"
# --- 可用工具定义 (OpenAI 函数调用格式) ---
TOOLS = [
    # 1. 内置天气工具 (直接 HTTP 请求)
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定经纬度的当前天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number", "description": "纬度"},
                    "longitude": {"type": "number", "description": "经度"}
                },
                "required": ["latitude", "longitude"]
            }
        }
    },
    # 2. open-internet MCP 汇总工具 (连接你安装的 MCP 服务器)
    {
        "type": "function",
        "function": {
            "name": "mcp_openinternet",
            "description": "调用 open-internet MCP 服务器中的任意工具。可查 Wikipedia、GitHub 搜索、学术论文等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "tool_name": {"type": "string", "description": "MCP 工具名称，如 wikipediaSearch, githubSearch, arxivSearch"},
                    "arguments": {"type": "object", "description": "传递给该工具的 JSON 参数，如 {'q': 'Qwen model'} 或 {'query': 'climate change'}"}
                },
                "required": ["tool_name", "arguments"]
            }
        }
    }
]
# --- 工具实现函数 ---
def execute_tool(tool_name: str, arguments: dict) -> str:
    """执行工具并返回 JSON 字符串结果"""
    # ---- 内置天气工具 ----
    if tool_name == "get_weather":
        lat = arguments.get("latitude")
        lon = arguments.get("longitude")
        if not lat or not lon:
            return json.dumps({"error": "Missing latitude or longitude"})
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        resp = requests.get(url)
        if resp.status_code == 200:
            return json.dumps(resp.json().get("current_weather", {}))
        return json.dumps({"error": f"HTTP {resp.status_code}"})
    # ---- open-internet MCP 工具 (通过 HTTP 转发) ----
    elif tool_name == "mcp_openinternet":
        inner_tool = arguments.get("tool_name")
        inner_args = arguments.get("arguments", {})
        if not inner_tool:
            return json.dumps({"error": "No inner tool_name provided"})
        # 连接到 open-internet MCP 服务器。默认 Stdio 模式需要子进程，
        # 这里改用 HTTP 模式 (如果 MCP 服务器支持) 或使用子进程。
        # 为简单起见，我们使用 requests 模拟 MCP 服务器的 HTTP 端点。
        # 你需根据实际 MCP 服务器配置调整此 URL。
        MCP_SERVER_URL = "http://localhost:3001/mcp"  # 示例端点，请根据实际情况修改
        payload = {
            "method": "tools/call",
            "params": {
                "name": inner_tool,
                "arguments": inner_args
            }
        }
        try:
            resp = requests.post(MCP_SERVER_URL, json=payload, timeout=10)
            if resp.status_code == 200:
                return json.dumps(resp.json())
            else:
                # 如果 MCP 服务器未运行或端点不对，回退到直接调用公开 API
                # 此处以 Wikipedia Summary 为例
                if inner_tool == "wikipediaSummary":
                    title = inner_args.get("title", "")
                    lang = inner_args.get("lang", "en")
                    wiki_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(title)}"
                    wiki_resp = requests.get(wiki_url)
                    if wiki_resp.status_code == 200:
                        return json.dumps(wiki_resp.json())
                    return json.dumps({"error": f"Wikipedia API error: {wiki_resp.status_code}"})
                return json.dumps({"error": f"Tool {inner_tool} not supported in fallback mode"})
        except Exception as e:
            return json.dumps({"error": str(e)})
    return json.dumps({"error": f"Unknown tool: {tool_name}"})
# --- 对话循环 ---
messages = []
print("本地 Agent 已启动 (输入 'exit' 退出)")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    messages.append({"role": "user", "content": user_input})
    # 第一次请求: 让模型决定是否调用工具
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto"  # 模型自行决定
    }
    resp = requests.post(LITELLM_URL, json=payload)
    if resp.status_code != 200:
        print(f"Error: {resp.text}")
        continue
    data = resp.json()
    msg = data["choices"][0]["message"]
    # 检查是否需要调用工具
    if msg.get("tool_calls"):
        tool_calls = msg["tool_calls"]
        # 将模型的工具调用请求加入对话
        messages.append(msg)
        # 执行每个工具调用
        for tc in tool_calls:
            tool_name = tc["function"]["name"]
            arguments = json.loads(tc["function"]["arguments"])
            print(f"[调用工具: {tool_name}] 参数: {arguments}")
            result = execute_tool(tool_name, arguments)
            print(f"[工具结果]: {result[:200]}...")  # 截断显示
            # 将工具结果加入对话
            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": result
            })
        # 第二次请求: 将工具结果发送给模型生成最终回答
        payload2 = {
            "model": MODEL_NAME,
            "messages": messages
        }
        resp2 = requests.post(LITELLM_URL, json=payload2)
        if resp2.status_code == 200:
            final_msg = resp2.json()["choices"][0]["message"]["content"]
            print(f"AI: {final_msg}")
            messages.append({"role": "assistant", "content": final_msg})
        else:
            print(f"Error: {resp2.text}")
    else:
        # 没有工具调用，直接输出回复
        print(f"AI: {msg.get('content', '')}")
        messages.append({"role": "assistant", "content": msg.get('content', '')})