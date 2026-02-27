# 🧪 QA Tester Agent - 全栈测试员系统

## 概述

基于你的需求构建的「测试员」Agent，具备四大核心能力：

1. ✅ **底层系统控制力** - Shell/进程/文件系统
2. ✅ **浏览器深度自动化** - Playwright + 控制台捕获 + 网络抓包
3. ✅ **视觉与多模态感知** - 截图 + AI 视觉分析
4. ✅ **结构化通信与调度配合** - JSON 输出 + Webhook

---

## 📁 文件结构

```
~/.openclaw/workspace/
├── qa_tester.py                      # 核心测试脚本
├── deploy_qa_tester.sh               # 部署脚本
├── qa_reports/                       # 测试报告输出目录
├── agents/
│   └── qa-tester.json               # Agent 配置
└── skills/
    └── qa-tester/
        ├── SKILL.md                 # 技能文档
        └── qa_tester_skill.py       # 技能接口
```

---

## 🚀 快速开始

### 1. 部署 QA Tester

```bash
cd ~/.openclaw/workspace
./deploy_qa_tester.sh
```

### 2. 测试本地项目

```bash
# 假设你的项目运行在 localhost:3000
python3 ~/.openclaw/workspace/qa_tester.py \
  --mode test \
  --url http://localhost:3000 \
  --output report.json
```

### 3. 查看结果

```bash
cat report.json | jq .
```

---

## 🔧 四大核心能力详解

### 1. 底层系统控制力

**Shell 命令执行:**
```python
import subprocess

# 安装依赖
subprocess.run(["npm", "install"], cwd="/path/to/project")

# 启动服务
process = subprocess.Popen(
    ["npm", "run", "dev"],
    cwd="/path/to/project"
)

# 监控进程
if process.poll() is None:
    print("服务运行中")
```

**文件系统访问:**
```python
from pathlib import Path

# 检查 package.json
package_json = Path("/path/to/project/package.json")
if package_json.exists():
    import json
    config = json.loads(package_json.read_text())
    print(f"启动脚本: {config['scripts']}")
```

### 2. 浏览器深度自动化

**控制台捕获:**
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    # 捕获控制台消息
    console_logs = []
    page.on("console", lambda msg: console_logs.append({
        "type": msg.type,
        "text": msg.text
    }))
    
    page.goto("http://localhost:3000")
    
    # 检查错误
    errors = [log for log in console_logs if log["type"] == "error"]
    if errors:
        print(f"发现 {len(errors)} 个控制台错误")
```

**网络抓包:**
```python
requests = []
responses = []

page.on("request", lambda req: requests.append({
    "url": req.url,
    "method": req.method
}))

page.on("response", lambda res: responses.append({
    "url": res.url,
    "status": res.status
}))

page.goto("http://localhost:3000")

# 检查失败请求
failed = [r for r in responses if r["status"] >= 400]
```

**DOM 交互:**
```python
# 点击元素
page.click("#login-btn")

# 输入文本
page.fill("#username", "admin")
page.fill("#password", "password")

# 滚动页面
page.evaluate("window.scrollTo(0, 500)")
```

### 3. 视觉与多模态感知

**截图:**
```python
# 可视区域截图
page.screenshot(path="screenshot.png")

# 全页截图
page.screenshot(path="fullpage.png", full_page=True)

# 元素截图
element = page.locator("#header")
element.screenshot(path="header.png")
```

**AI 视觉分析 (配合多模态模型):**
```python
# 截图后发送给 Claude/GPT-4o 分析
screenshot_path = "page.png"
page.screenshot(path=screenshot_path)

# 然后使用 OpenClaw 的多模态能力分析
# 作为 Agent 时，模型可以直接看到截图
```

### 4. 结构化通信与调度配合

**JSON 输出:**
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
        "text": "TypeError: Cannot read property 'x' of undefined"
      }
    ],
    "failed_requests": [
      {
        "url": "/api/data",
        "status": 500
      }
    ]
  },
  "screenshot_path": "/path/to/screenshot.png"
}
```

**Webhook 接收:**
```python
# 启动 WebSocket 服务器
async def handle_command(websocket, path):
    async for message in websocket:
        command = json.loads(message)
        
        if command["type"] == "test_url":
            result = run_test(command["url"])
            await websocket.send(json.dumps(result))
```

---

## 🔗 与 LangGraph/管家程序集成

### HTTP API 调用示例

```python
import requests
import json

# 调用 QA Tester
response = requests.post("http://localhost:8765/test", json={
    "url": "http://localhost:3000",
    "type": "comprehensive",
    "wait_for": "networkidle"
})

result = response.json()

# 根据结果决策
if result["status"] == "failed":
    if result["details"]["console_errors"]:
        # 前端报错，通知程序员修复
        notify_programmer({
            "type": "frontend_error",
            "errors": result["details"]["console_errors"]
        })
    
    if result["details"]["failed_requests"]:
        # API 报错，通知后端修复
        notify_programmer({
            "type": "backend_error",
            "errors": result["details"]["failed_requests"]
        })
```

### LangGraph 状态机集成

```python
from langgraph.graph import StateGraph
from typing import TypedDict

class QAState(TypedDict):
    url: str
    test_result: dict
    action: str  # "fix", "approve", "retry"

def qa_test_node(state: QAState):
    """QA 测试节点"""
    result = call_qa_tester(state["url"])
    return {"test_result": result}

def decision_node(state: QAState):
    """决策节点"""
    if state["test_result"]["status"] == "passed":
        return {"action": "approve"}
    else:
        return {"action": "fix"}

def notify_programmer_node(state: QAState):
    """通知程序员"""
    send_to_openclaw_programmer(state["test_result"])
    return state

# 构建工作流
workflow = StateGraph(QAState)
workflow.add_node("test", qa_test_node)
workflow.add_node("decide", decision_node)
workflow.add_node("notify", notify_programmer_node)

workflow.set_entry_point("test")
workflow.add_edge("test", "decide")
workflow.add_conditional_edges(
    "decide",
    lambda s: s["action"],
    {
        "approve": END,
        "fix": "notify"
    }
)
workflow.add_edge("notify", END)

app = workflow.compile()
```

---

## 🎯 使用场景示例

### 场景 1: CI/CD 自动化测试

```yaml
# .github/workflows/qa.yml
name: QA Tests
on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Start dev server
        run: npm run dev &
        
      - name: Wait for server
        run: sleep 10
        
      - name: Run QA Tests
        run: |
          python3 qa_tester.py --mode test \
            --url http://localhost:3000 \
            --output qa-report.json
            
      - name: Check Results
        run: |
          STATUS=$(cat qa-report.json | jq -r '.status')
          if [ "$STATUS" != "passed" ]; then
            echo "QA failed!"
            cat qa-report.json | jq '.details.console_errors'
            exit 1
          fi
```

### 场景 2: 程序员提交代码后的自动验收

```python
# 管家程序调度逻辑
def on_code_submitted(programmer_output):
    """程序员提交代码后触发"""
    
    # 1. 启动本地服务
    start_dev_server()
    
    # 2. 调用 QA Tester
    result = qa_tester.test_url("http://localhost:3000")
    
    # 3. 根据结果处理
    if result["status"] == "passed":
        # 验收通过，合并代码
        merge_code()
        notify_user("✅ 代码验收通过，已合并")
    else:
        # 验收失败，通知程序员修复
        feedback = generate_feedback(result)
        notify_programmer(feedback)
```

### 场景 3: 视觉 QA

```python
# 视觉验收
requirements = """
- 登录按钮必须是蓝色的
- 按钮应该居中对齐
- 表单宽度不超过 400px
"""

result = qa_tester.visual_qa(
    url="http://localhost:3000/login",
    requirements=requirements
)

# 截图发送给多模态模型分析
analysis = claude_analyze_image(
    image_path=result["screenshot_path"],
    prompt=f"检查以下要求是否满足:\n{requirements}"
)
```

---

## 📊 输出字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | "passed", "failed", "error" |
| `test_type` | string | "comprehensive", "functional", "visual" |
| `url` | string | 测试的 URL |
| `timestamp` | string | ISO 8601 格式时间 |
| `duration_ms` | int | 测试耗时（毫秒）|
| `details.console_errors` | array | 控制台错误列表 |
| `details.failed_requests` | array | 失败的网络请求 |
| `details.page_title` | string | 页面标题 |
| `screenshot_path` | string | 截图文件路径 |

---

## 🛠️ 扩展开发

### 添加自定义测试规则

```python
from qa_tester import QATester

class MyTester(QATester):
    def test_performance(self, url):
        """测试页面性能"""
        self.start_browser()
        self.page.goto(url)
        
        # 获取性能指标
        metrics = self.page.evaluate("""() => {
            return JSON.parse(JSON.stringify(performance.timing))
        }""")
        
        load_time = metrics['loadEventEnd'] - metrics['navigationStart']
        
        return {
            "status": "passed" if load_time < 3000 else "failed",
            "load_time_ms": load_time
        }
```

### 集成更多工具

```python
# 集成 Lighthouse 性能测试
subprocess.run([
    "lighthouse", url,
    "--output=json",
    "--chrome-flags='--headless'"
])
```

---

## 🔮 未来扩展

- [ ] 移动端测试支持
- [ ] 并发测试能力
- [ ] 测试历史记录
- [ ] 自动修复建议
- [ ] 与更多 CI/CD 平台集成

---

**QA Tester Agent 已准备就绪！** 🎉

运行 `./deploy_qa_tester.sh` 开始部署。
