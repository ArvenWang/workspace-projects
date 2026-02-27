---
name: qa-tester
description: |
  QA 测试员 Agent - 具备四大核心能力的全栈测试系统
  
  能力包括：
  1. 底层系统控制 (Shell/进程/文件系统)
  2. 浏览器深度自动化 (Playwright + 控制台捕获 + 网络抓包)
  3. 视觉与多模态感知 (截图 + AI分析)
  4. 结构化通信 (JSON输出 + Webhook)
  
  用于自动化前端验收测试、Bug检测、视觉QA
---

# QA Tester Agent

## 核心能力

### 1. 底层系统控制
- ✅ Shell 命令执行
- ✅ 进程监控
- ✅ 文件系统访问

### 2. 浏览器深度自动化
- ✅ Playwright 浏览器控制
- ✅ 控制台捕获 (console.error/warning)
- ✅ 网络抓包 (XHR/Fetch 监控)
- ✅ DOM 交互 (点击、输入、滚动)

### 3. 视觉 QA
- ✅ 页面截图
- ✅ 全页截图
- ✅ 支持多模态模型分析（需配合 Claude/GPT-4o）

### 4. 结构化通信
- ✅ JSON 格式输出
- ✅ Webhook 接收指令
- ✅ 标准化测试报告

## 使用方法

### 快速测试 URL
```bash
# 测试本地开发服务器
python3 ~/.openclaw/workspace/qa_tester.py --mode test --url http://localhost:3000

# 带可视化窗口测试
python3 ~/.openclaw/workspace/qa_tester.py --mode test --url http://localhost:3000 --headed

# 输出到文件
python3 ~/.openclaw/workspace/qa_tester.py --mode test --url http://localhost:3000 --output report.json
```

### 作为 Agent 使用
```python
from qa_tester import QATester

# 创建测试员
tester = QATester()

# 启动浏览器
tester.start_browser(headless=True)

# 测试 URL
result = tester.test_url("http://localhost:3000")

# 检查结果
print(f"状态: {result.status}")
print(f"控制台错误: {result.details.get('console_errors', [])}")
print(f"网络失败: {result.details.get('failed_requests', [])}")

# 关闭
tester.close()
```

### 用户流程测试
```python
actions = [
    {"type": "click", "selector": "#login-btn"},
    {"type": "type", "selector": "#username", "text": "admin"},
    {"type": "type", "selector": "#password", "text": "password"},
    {"type": "click", "selector": "#submit"},
    {"type": "wait", "delay": 2000},
    {"type": "screenshot"}
]

result = tester.run_user_flow("http://localhost:3000/login", actions)
```

### 启动 Webhook 服务器
```bash
python3 ~/.openclaw/workspace/qa_tester.py --mode server
```

然后通过 WebSocket 发送指令：
```json
{
  "type": "test_url",
  "url": "http://localhost:3000",
  "headless": true
}
```

## 输出格式

### 测试结果 JSON
```json
{
  "status": "failed",
  "test_type": "comprehensive",
  "url": "http://localhost:3000",
  "timestamp": "2024-01-15T10:30:00",
  "duration_ms": 3500,
  "details": {
    "console_errors": [
      {
        "type": "error",
        "text": "TypeError: Cannot read property 'x' of undefined",
        "location": {...}
      }
    ],
    "console_warnings": [...],
    "failed_requests": [
      {
        "url": "/api/data",
        "status": 500,
        "status_text": "Internal Server Error"
      }
    ],
    "page_title": "My App",
    "page_url": "http://localhost:3000"
  },
  "screenshot_path": "/Users/.../qa_reports/screenshot_123.png"
}
```

## 与 LangGraph/管家程序集成

### HTTP API 调用
```python
import requests

# 触发测试
response = requests.post("http://localhost:8765/test", json={
    "url": "http://localhost:3000",
    "type": "comprehensive"
})

result = response.json()

# 根据结果决策
if result["status"] == "failed":
    if result["details"]["console_errors"]:
        # 有前端报错，通知程序员修复
        pass
    if result["details"]["failed_requests"]:
        # 有 API 报错，通知后端修复
        pass
```

### WebSocket 实时通信
```python
import asyncio
import websockets
import json

async def run_test():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "type": "test_url",
            "url": "http://localhost:3000"
        }))
        
        result = await websocket.recv()
        data = json.loads(result)
        
        print(f"测试完成: {data['status']}")

asyncio.run(run_test())
```

## 安装依赖

```bash
# Playwright
pip3 install playwright
python3 -m playwright install chromium

# WebSocket 支持 (用于 Webhook 服务器)
pip3 install websockets
```

## 配置环境变量

```bash
# QA 报告输出目录
export QA_REPORTS_DIR="~/.openclaw/workspace/qa_reports"

# Webhook 服务器配置
export QA_WEBHOOK_HOST="localhost"
export QA_WEBHOOK_PORT="8765"
```

## 故障排查

### Playwright 未安装
```bash
pip3 install playwright
python3 -m playwright install
```

### 浏览器启动失败
```bash
# 尝试可视化模式查看错误
python3 qa_tester.py --mode test --url http://localhost:3000 --headed
```

### 端口被占用
```bash
# 更换 Webhook 端口
python3 qa_tester.py --mode server --port 8766
```

## 进阶用法

### 自定义测试规则
```python
class CustomTester(QATester):
    def custom_validation(self, page):
        # 自定义验证逻辑
        title = page.title()
        if "Error" in title:
            return {"status": "failed", "reason": "Page has error in title"}
        return {"status": "passed"}
```

### CI/CD 集成
```yaml
# .github/workflows/qa.yml
- name: Run QA Tests
  run: |
    python3 qa_tester.py --mode test --url http://localhost:3000 --output qa-report.json
    
- name: Check Results
  run: |
    STATUS=$(cat qa-report.json | jq -r '.status')
    if [ "$STATUS" != "passed" ]; then
      echo "QA failed!"
      exit 1
    fi
```
