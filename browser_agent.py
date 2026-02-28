#!/usr/bin/env python3
"""
浏览器自动化Agent
能帮你做什么：
1. 自动浏览网页
2. 提取网页信息
3. 填表、点击操作
4. 截图分析

使用方法：
python3 browser_agent.py "帮我搜索北京天气"
"""

import asyncio
import json
import sys
from playwright.async_api import async_playwright

# 配置
CONFIG = {
    'headless': False,  # 是否无头模式
    'viewport': {'width': 1920, 'height': 1080},
}

async def browse(url: str, action: str = None):
    """浏览网页并执行操作"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=CONFIG['headless'])
        page = await browser.new_page(viewport=CONFIG['viewport'])
        
        print(f"🌐 打开: {url}")
        await page.goto(url, wait_until='networkidle')
        
        if action:
            print(f"⚡ 执行: {action}")
            # 根据动作类型执行
            if '截图' in action:
                await page.screenshot(path='screenshot.png')
                print("📸 截图已保存")
            elif '点击' in action:
                # 简单实现
                pass
        
        # 提取页面内容
        content = await page.content()
        title = await page.title()
        
        await browser.close()
        
        return {
            'title': title,
            'url': url,
            'content_length': len(content)
        }

async def search(query: str, engine: str = 'google'):
    """搜索功能"""
    engines = {
        'google': 'https://www.google.com/search?q=',
        'baidu': 'https://www.baidu.com/s?wd=',
        'bing': 'https://www.bing.com/search?q='
    }
    
    url = f"{engines.get(engine, engines['google'])}{query}"
    return await browse(url, '搜索')

async def extract_info(url: str, selectors: list = None):
    """提取网页特定信息"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=CONFIG['headless'])
        page = await browser.new_page()
        await page.goto(url, wait_until='networkidle')
        
        results = []
        
        if selectors:
            for sel in selectors:
                elements = await page.query_selector_all(sel)
                for el in elements:
                    text = await el.inner_text()
                    results.append(text)
        
        await browser.close()
        return results

async def fill_form(url: str, data: dict):
    """自动填表"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=CONFIG['headless'])
        page = await browser.new_page()
        await page.goto(url)
        
        for field, value in data.items():
            try:
                await page.fill(f'[name="{field}"]', value)
                print(f"✅ 填写: {field} = {value}")
            except Exception as e:
                print(f"❌ 失败: {field} - {e}")
        
        await browser.close()
        return True

# CLI入口
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 browser_agent.py search <关键词>")
        print("  python3 browser_agent.py browse <URL>")
        print("  python3 browser_agent.py fill <URL> <field>=<value>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'search' and len(sys.argv) > 2:
        query = sys.argv[2]
        result = asyncio.run(search(query))
        print(f"✅ 搜索完成: {result['title']}")
    
    elif cmd == 'browse' and len(sys.argv) > 2:
        url = sys.argv[2]
        result = asyncio.run(browse(url))
        print(f"✅ 打开: {result['title']}")
    
    elif cmd == 'fill' and len(sys.argv) > 3:
        url = sys.argv[2]
        data = {}
        for arg in sys.argv[3:]:
            if '=' in arg:
                k, v = arg.split('=', 1)
                data[k] = v
        result = asyncio.run(fill_form(url, data))
        print(f"✅ 填表完成")
    
    else:
        print("命令错误")
