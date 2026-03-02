#!/usr/bin/env python3
"""
OpenClaw 浏览器控制技能
使用浏览器桥接控制用户已登录的浏览器

功能:
- 执行任意 JS
- 扫描页面
- 点击元素
- 填写表单
- 截图 (需要额外依赖)

使用:
    python3 -m browser_bridge scan     # 扫描当前页面
    python3 -m browser_bridge exec "document.title"  # 执行 JS
    python3 -m browser_bridge click "#submit"  # 点击元素
    python3 -m browser_bridge fill "input[name=q]" "搜索内容"  # 填写表单
"""

import asyncio
import json
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from browser_bridge import BrowserBridge


async def scan(bridge: BrowserBridge):
    """扫描页面"""
    try:
        result = await bridge.scan_page()
        print(f"📄 页面标题: {result.get('title')}")
        print(f"🔗 URL: {result.get('url')}")
        print(f"\n📋 链接 (前10个):")
        for i, link in enumerate(result.get('links', [])[:10], 1):
            print(f"  {i}. {link.get('text')[:40]} -> {link.get('href')[:60]}")
        return result
    except Exception as e:
        print(f"❌ 扫描失败: {e}")
        return None


async def exec_js(bridge: BrowserBridge, code: str):
    """执行 JS"""
    try:
        result = await bridge.execute_js(code)
        print(f"✅ 执行结果: {result}")
        return result
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return None


async def click(bridge: BrowserBridge, selector: str):
    """点击元素"""
    code = f"""
(function() {{
    const el = document.querySelector('{selector}');
    if (el) {{
        el.click();
        return '✅ 已点击: {selector}';
    }}
    return '❌ 未找到: {selector}';
}})();
"""
    return await exec_js(bridge, code)


async def fill(bridge: BrowserBridge, selector: str, value: str):
    """填写表单"""
    # 转义反引号
    value_escaped = value.replace('`', '\\`')
    code = f"""
(function() {{
    const el = document.querySelector('{selector}');
    if (el) {{
        el.value = `{value_escaped}`;
        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
        return '✅ 已填写: {selector} = {value}';
    }}
    return '❌ 未找到: {selector}';
}})();
"""
    return await exec_js(bridge, code)


async def list_sessions(bridge: BrowserBridge):
    """列出所有会话"""
    sessions = bridge.get_sessions()
    if not sessions:
        print("❌ 没有活跃的浏览器会话")
        print("💡 请确保浏览器已安装 Tampermonkey + openclaw_browser_bridge.user.js")
        return
    
    print(f"📱 活跃会话 ({len(sessions)} 个):")
    for s in sessions:
        print(f"  - {s['id']}: {s['title']}")
        print(f"    {s['url']}")
        print(f"    最后活动: {s['last_seen']}")


async def interactive(bridge: BrowserBridge):
    """交互模式"""
    print("🔌 OpenClaw 浏览器控制 (输入 'help' 查看命令)")
    print("=" * 50)
    
    while True:
        try:
            cmd = input("\n> ").strip()
            
            if not cmd:
                continue
            elif cmd in ['exit', 'quit', 'q']:
                print("👋 再见!")
                break
            elif cmd in ['help', 'h']:
                print("""
命令:
  scan, s        - 扫描当前页面
  ls, list       - 列出活跃会话
  click <sel>    - 点击 CSS 选择器元素
  fill <sel> <v> - 填写表单
  exec <js>      - 执行 JS 代码
  clear          - 清屏
  exit           - 退出
""")
            elif cmd in ['scan', 's']:
                await scan(bridge)
            elif cmd in ['ls', 'list']:
                await list_sessions(bridge)
            elif cmd.startswith('click '):
                selector = cmd[6:].strip()
                await click(bridge, selector)
            elif cmd.startswith('fill '):
                parts = cmd[5:].split(None, 1)
                if len(parts) == 2:
                    selector, value = parts
                    await fill(bridge, selector, value)
                else:
                    print("用法: fill <selector> <value>")
            elif cmd.startswith('exec '):
                code = cmd[5:]
                await exec_js(bridge, code)
            elif cmd in ['clear', 'cls']:
                os.system('clear' if os.name == 'posix' else 'cls')
            else:
                # 尝试作为 JS 执行
                await exec_js(bridge, cmd)
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenClaw 浏览器桥接')
    parser.add_argument('--host', default='localhost', help='服务器地址')
    parser.add_argument('--port', type=int, default=18765, help='服务器端口')
    parser.add_argument('--scan', '-s', action='store_true', help='扫描页面')
    parser.add_argument('--execute', '-e', help='执行 JS 代码')
    parser.add_argument('--click', help='点击元素 (CSS 选择器)')
    parser.add_argument('--fill', nargs=2, metavar=('SEL', 'VAL'), help='填写表单')
    parser.add_argument('--list', '-l', action='store_true', help='列出会话')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')
    
    args = parser.parse_args()
    
    bridge = BrowserBridge(args.host, args.port)
    
    # 如果不是服务器模式，尝试连接
    if not args.interactive and not args.list:
        if args.scan:
            async with __import__('websockets').connect(f'ws://{args.host}:{args.port}') as ws:
                await asyncio.sleep(1)
                if bridge.default_session:
                    await scan(bridge)
                else:
                    print("❌ 没有活跃的会话")
        elif args.execute:
            async with __import__('websockets').connect(f'ws://{args.host}:{args.port}') as ws:
                await asyncio.sleep(1)
                if bridge.default_session:
                    await exec_js(bridge, args.execute)
                else:
                    print("❌ 没有活跃的会话")
        elif args.click:
            async with __import__('websockets').connect(f'ws://{args.host}:{args.port}') as ws:
                await asyncio.sleep(1)
                if bridge.default_session:
                    await click(bridge, args.click)
                else:
                    print("❌ 没有活跃的会话")
        elif args.fill:
            async with __import__('websockets').connect(f'ws://{args.host}:{args.port}') as ws:
                await asyncio.sleep(1)
                if bridge.default_session:
                    await fill(bridge, args.fill[0], args.fill[1])
                else:
                    print("❌ 没有活跃的会话")
        else:
            parser.print_help()
    elif args.list:
        async with __import__('websockets').connect(f'ws://{args.host}:{args.port}') as ws:
            await asyncio.sleep(1)
            await list_sessions(bridge)
    else:
        # 启动服务器
        await bridge.start()


if __name__ == '__main__':
    asyncio.run(main())
