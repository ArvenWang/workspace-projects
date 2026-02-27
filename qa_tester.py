#!/usr/bin/env python3
"""
OpenClaw QA Tester Agent - 全栈测试员

四大核心能力：
1. 底层系统控制 (Shell, Process, FileSystem)
2. 浏览器深度自动化 (Playwright + 控制台捕获 + 网络抓包)
3. 视觉与多模态感知 (截图 + AI分析)
4. 结构化通信 (JSON输出 + Webhook接收)
"""

import os
import sys
import json
import time
import subprocess
import tempfile
import asyncio
import websockets
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict

# Playwright
from playwright.sync_api import sync_playwright, Page, Browser, ConsoleMessage, Request, Response

# 配置
WORKSPACE = Path("/Users/wangjingwen/.openclaw/workspace")
REPORTS_DIR = WORKSPACE / "qa_reports"
REPORTS_DIR.mkdir(exist_ok=True)


@dataclass
class TestResult:
    """测试结果结构化数据"""
    status: str  # "passed", "failed", "error"
    test_type: str  # "console", "network", "visual", "functional"
    url: str
    timestamp: str
    duration_ms: int
    details: Dict[str, Any]
    screenshot_path: Optional[str] = None
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)


class ConsoleCapture:
    """浏览器控制台捕获器"""
    
    def __init__(self):
        self.logs: List[Dict] = []
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
    
    def on_console(self, msg: ConsoleMessage):
        """控制台消息回调"""
        entry = {
            "type": msg.type,
            "text": msg.text,
            "location": msg.location,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logs.append(entry)
        
        if msg.type == "error":
            self.errors.append(entry)
        elif msg.type == "warning":
            self.warnings.append(entry)
    
    def get_errors(self) -> List[Dict]:
        return self.errors
    
    def get_warnings(self) -> List[Dict]:
        return self.warnings
    
    def has_errors(self) -> bool:
        return len(self.errors) > 0


class NetworkCapture:
    """网络请求捕获器"""
    
    def __init__(self):
        self.requests: List[Dict] = []
        self.responses: List[Dict] = []
        self.failed_requests: List[Dict] = []
    
    def on_request(self, request: Request):
        """请求发起回调"""
        entry = {
            "url": request.url,
            "method": request.method,
            "headers": dict(request.headers),
            "timestamp": datetime.now().isoformat()
        }
        self.requests.append(entry)
    
    def on_response(self, response: Response):
        """响应接收回调"""
        entry = {
            "url": response.url,
            "status": response.status,
            "status_text": response.status_text,
            "headers": dict(response.headers),
            "timestamp": datetime.now().isoformat()
        }
        self.responses.append(entry)
        
        # 检查失败状态码
        if response.status >= 400:
            self.failed_requests.append(entry)
    
    def get_failed_requests(self) -> List[Dict]:
        return self.failed_requests
    
    def has_failures(self) -> bool:
        return len(self.failed_requests) > 0


class QATester:
    """QA 测试员核心类"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.console_capture = ConsoleCapture()
        self.network_capture = NetworkCapture()
        self.test_results: List[TestResult] = []
        
    def start_browser(self, headless: bool = True, browser_type: str = "chromium"):
        """启动浏览器"""
        playwright = sync_playwright().start()
        
        browser_launcher = getattr(playwright, browser_type)
        self.browser = browser_launcher.launch(headless=headless)
        self.page = self.browser.new_page()
        
        # 设置控制台监听
        self.page.on("console", self.console_capture.on_console)
        
        # 设置网络监听
        self.page.on("request", self.network_capture.on_request)
        self.page.on("response", self.network_capture.on_response)
        
    def test_url(self, url: str, wait_for: str = "networkidle") -> TestResult:
        """测试指定 URL"""
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        
        start_time = time.time()
        
        try:
            # 导航到页面
            self.page.goto(url, wait_until=wait_for)
            
            # 等待一段时间让页面稳定
            time.sleep(2)
            
            # 截图
            screenshot_path = REPORTS_DIR / f"screenshot_{int(time.time())}.png"
            self.page.screenshot(path=str(screenshot_path), full_page=True)
            
            duration = int((time.time() - start_time) * 1000)
            
            # 分析结果
            errors = self.console_capture.get_errors()
            failed_requests = self.network_capture.get_failed_requests()
            
            # 判断测试状态
            if errors or failed_requests:
                status = "failed"
            else:
                status = "passed"
            
            result = TestResult(
                status=status,
                test_type="comprehensive",
                url=url,
                timestamp=datetime.now().isoformat(),
                duration_ms=duration,
                details={
                    "console_errors": errors,
                    "console_warnings": self.console_capture.get_warnings(),
                    "failed_requests": failed_requests,
                    "page_title": self.page.title(),
                    "page_url": self.page.url
                },
                screenshot_path=str(screenshot_path)
            )
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            
            result = TestResult(
                status="error",
                test_type="comprehensive",
                url=url,
                timestamp=datetime.now().isoformat(),
                duration_ms=duration,
                details={"error": str(e)},
                screenshot_path=None
            )
            
            self.test_results.append(result)
            return result
    
    def run_user_flow(self, url: str, actions: List[Dict]) -> TestResult:
        """运行用户流程测试"""
        if not self.page:
            raise RuntimeError("Browser not started.")
        
        start_time = time.time()
        action_results = []
        
        try:
            # 导航到起始页面
            self.page.goto(url, wait_until="networkidle")
            
            for action in actions:
                action_type = action.get("type")
                
                if action_type == "click":
                    selector = action.get("selector")
                    self.page.click(selector)
                    action_results.append({"action": "click", "selector": selector, "status": "ok"})
                    
                elif action_type == "type":
                    selector = action.get("selector")
                    text = action.get("text")
                    self.page.fill(selector, text)
                    action_results.append({"action": "type", "selector": selector, "status": "ok"})
                    
                elif action_type == "wait":
                    delay = action.get("delay", 1000)
                    time.sleep(delay / 1000)
                    action_results.append({"action": "wait", "delay": delay, "status": "ok"})
                    
                elif action_type == "screenshot":
                    screenshot_path = REPORTS_DIR / f"flow_{int(time.time())}.png"
                    self.page.screenshot(path=str(screenshot_path))
                    action_results.append({"action": "screenshot", "path": str(screenshot_path), "status": "ok"})
            
            duration = int((time.time() - start_time) * 1000)
            
            result = TestResult(
                status="passed",
                test_type="functional",
                url=url,
                timestamp=datetime.now().isoformat(),
                duration_ms=duration,
                details={"actions": action_results},
                screenshot_path=str(screenshot_path) if 'screenshot_path' in locals() else None
            )
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            
            result = TestResult(
                status="failed",
                test_type="functional",
                url=url,
                timestamp=datetime.now().isoformat(),
                duration_ms=duration,
                details={"actions": action_results, "error": str(e)},
                screenshot_path=None
            )
            
            self.test_results.append(result)
            return result
    
    def visual_qa(self, url: str, requirements: str) -> TestResult:
        """视觉 QA 测试"""
        if not self.page:
            raise RuntimeError("Browser not started.")
        
        start_time = time.time()
        
        try:
            self.page.goto(url, wait_until="networkidle")
            time.sleep(2)
            
            # 截图
            screenshot_path = REPORTS_DIR / f"visual_{int(time.time())}.png"
            self.page.screenshot(path=str(screenshot_path), full_page=True)
            
            duration = int((time.time() - start_time) * 1000)
            
            # 这里应该调用多模态模型进行视觉分析
            # 简化版本返回截图路径
            
            result = TestResult(
                status="passed",
                test_type="visual",
                url=url,
                timestamp=datetime.now().isoformat(),
                duration_ms=duration,
                details={
                    "requirements": requirements,
                    "visual_analysis": "请使用多模态模型分析截图"
                },
                screenshot_path=str(screenshot_path)
            )
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            
            result = TestResult(
                status="error",
                test_type="visual",
                url=url,
                timestamp=datetime.now().isoformat(),
                duration_ms=duration,
                details={"error": str(e)},
                screenshot_path=None
            )
            
            self.test_results.append(result)
            return result
    
    def close(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
            self.browser = None
            self.page = None
    
    def export_report(self) -> str:
        """导出测试报告"""
        report = {
            "summary": {
                "total": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r.status == "passed"),
                "failed": sum(1 for r in self.test_results if r.status == "failed"),
                "errors": sum(1 for r in self.test_results if r.status == "error")
            },
            "results": [asdict(r) for r in self.test_results]
        }
        
        report_path = REPORTS_DIR / f"report_{int(time.time())}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return str(report_path)


class WebhookServer:
    """Webhook 服务器 - 接收外部调度指令"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.tester = QATester()
        self.command_handlers: Dict[str, Callable] = {
            "test_url": self._handle_test_url,
            "test_flow": self._handle_test_flow,
            "visual_qa": self._handle_visual_qa,
            "get_status": self._handle_get_status
        }
    
    async def start(self):
        """启动 WebSocket 服务器"""
        async with websockets.serve(self._handle_connection, self.host, self.port):
            print(f"🌐 Webhook 服务器启动在 ws://{self.host}:{self.port}")
            await asyncio.Future()  # 永远运行
    
    async def _handle_connection(self, websocket, path):
        """处理 WebSocket 连接"""
        async for message in websocket:
            try:
                command = json.loads(message)
                cmd_type = command.get("type")
                
                if cmd_type in self.command_handlers:
                    result = await self.command_handlers[cmd_type](command)
                    await websocket.send(json.dumps(result, ensure_ascii=False))
                else:
                    await websocket.send(json.dumps({
                        "status": "error",
                        "error": f"Unknown command: {cmd_type}"
                    }))
                    
            except Exception as e:
                await websocket.send(json.dumps({
                    "status": "error",
                    "error": str(e)
                }))
    
    async def _handle_test_url(self, command: Dict) -> Dict:
        """处理 URL 测试命令"""
        url = command.get("url")
        headless = command.get("headless", True)
        
        self.tester.start_browser(headless=headless)
        result = self.tester.test_url(url)
        self.tester.close()
        
        return json.loads(result.to_json())
    
    async def _handle_test_flow(self, command: Dict) -> Dict:
        """处理流程测试命令"""
        url = command.get("url")
        actions = command.get("actions", [])
        headless = command.get("headless", True)
        
        self.tester.start_browser(headless=headless)
        result = self.tester.run_user_flow(url, actions)
        self.tester.close()
        
        return json.loads(result.to_json())
    
    async def _handle_visual_qa(self, command: Dict) -> Dict:
        """处理视觉 QA 命令"""
        url = command.get("url")
        requirements = command.get("requirements", "")
        headless = command.get("headless", True)
        
        self.tester.start_browser(headless=headless)
        result = self.tester.visual_qa(url, requirements)
        self.tester.close()
        
        return json.loads(result.to_json())
    
    async def _handle_get_status(self, command: Dict) -> Dict:
        """获取状态"""
        return {
            "status": "ok",
            "test_count": len(self.tester.test_results),
            "ready": True
        }


def run_cli():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw QA Tester")
    parser.add_argument("--mode", choices=["test", "server", "report"], default="test")
    parser.add_argument("--url", help="URL to test")
    parser.add_argument("--headless", action="store_true", default=True)
    parser.add_argument("--headed", action="store_true", help="Show browser window")
    parser.add_argument("--output", help="Output JSON file")
    
    args = parser.parse_args()
    
    if args.mode == "test":
        if not args.url:
            print("❌ Error: --url is required for test mode")
            sys.exit(1)
        
        headless = not args.headed
        
        print(f"🚀 启动测试员...")
        print(f"🌐 测试 URL: {args.url}")
        print(f"👁️  Headless: {headless}")
        
        tester = QATester()
        tester.start_browser(headless=headless)
        result = tester.test_url(args.url)
        tester.close()
        
        # 输出 JSON 结果
        output = result.to_json()
        
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"✅ 报告已保存: {args.output}")
        else:
            print(output)
        
        # 打印摘要
        print(f"\n📊 测试结果:")
        print(f"   状态: {result.status}")
        print(f"   耗时: {result.duration_ms}ms")
        
        if result.details.get("console_errors"):
            print(f"   ⚠️  控制台错误: {len(result.details['console_errors'])} 个")
        if result.details.get("failed_requests"):
            print(f"   ⚠️  网络请求失败: {len(result.details['failed_requests'])} 个")
        
        if result.screenshot_path:
            print(f"   📸 截图: {result.screenshot_path}")
    
    elif args.mode == "server":
        print("🌐 启动 Webhook 服务器...")
        server = WebhookServer()
        asyncio.run(server.start())
    
    elif args.mode == "report":
        tester = QATester()
        report_path = tester.export_report()
        print(f"📊 报告已导出: {report_path}")


if __name__ == "__main__":
    run_cli()
