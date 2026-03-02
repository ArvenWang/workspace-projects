#!/usr/bin/env python3
"""
漫剧平台权限测试脚本
测试各主流平台的可访问性、反爬机制、登录需求
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright


class PlatformTester:
    """平台权限测试器"""
    
    def __init__(self):
        self.results = []
        self.test_dir = Path(__file__).parent.parent.parent / "data" / "test_results"
        self.test_dir.mkdir(parents=True, exist_ok=True)
    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.browser.close()
        await self.playwright.stop()
    
    async def test_platform(self, name, url, selectors=None, test_login=False):
        """测试单个平台"""
        print(f"\n{'='*60}")
        print(f"🧪 测试平台: {name}")
        print(f"{'='*60}")
        
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        result = {
            'platform': name,
            'url': url,
            'test_time': datetime.now().isoformat(),
            'status': 'unknown',
            'details': {},
            'screenshots': []
        }
        
        try:
            print(f"🌐 访问: {url}")
            response = await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 基本信息
            result['details']['status_code'] = response.status if response else 'unknown'
            result['details']['final_url'] = page.url
            result['details']['title'] = await page.title()
            
            print(f"  ✓ 页面标题: {result['details']['title']}")
            print(f"  ✓ 状态码: {result['details']['status_code']}")
            print(f"  ✓ 最终URL: {result['details']['final_url']}")
            
            # 等待页面渲染
            await page.wait_for_timeout(3000)
            
            # 检查登录需求
            login_indicators = [
                '登录', 'login', '注册', 'signup', 'sign in', '请登录',
                '手机号', '验证码', '密码'
            ]
            
            page_content = await page.content()
            requires_login = any(indicator in page_content for indicator in login_indicators)
            
            result['details']['requires_login'] = requires_login
            if requires_login:
                print(f"  ⚠️ 可能需要登录")
                result['status'] = 'login_required'
            else:
                print(f"  ✓ 无需登录即可访问")
                result['status'] = 'accessible'
            
            # 检查反爬机制
            anti_crawl_indicators = [
                '访问频繁', '请稍后再试', '验证码', 'captcha', 'robot',
                '403', 'Forbidden', '请验证', '人机验证'
            ]
            
            has_anti_crawl = any(indicator in page_content for indicator in anti_crawl_indicators)
            result['details']['anti_crawl_detected'] = has_anti_crawl
            
            if has_anti_crawl:
                print(f"  ⚠️ 检测到反爬机制")
                result['status'] = 'anti_crawl'
            
            # 测试选择器（如果提供）
            if selectors:
                print(f"\n🔍 测试数据提取:")
                for selector_name, selector in selectors.items():
                    try:
                        elements = await page.query_selector_all(selector)
                        count = len(elements)
                        print(f"  • {selector_name}: {count}个元素")
                        result['details'][f'{selector_name}_count'] = count
                    except Exception as e:
                        print(f"  • {selector_name}: 失败 - {str(e)}")
                        result['details'][f'{selector_name}_error'] = str(e)
            
            # 截图保存
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = self.test_dir / f"{name}_{timestamp}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            result['screenshots'].append(str(screenshot_path))
            print(f"\n📸 截图已保存: {screenshot_path}")
            
        except Exception as e:
            print(f"  ❌ 测试失败: {str(e)}")
            result['status'] = 'error'
            result['details']['error'] = str(e)
        
        finally:
            await context.close()
        
        self.results.append(result)
        return result
    
    async def test_bilibili(self):
        """测试B站短剧分区"""
        selectors = {
            'video_cards': '.video-card, .bili-video-card, .video-list-item',
            'titles': 'h3, .title, a[title]',
            'play_counts': '.play-text, .view, .play-count'
        }
        
        return await self.test_platform(
            'B站短剧',
            'https://www.bilibili.com/v/channel/shortplay',
            selectors
        )
    
    async def test_xiaohongshu(self):
        """测试小红书"""
        selectors = {
            'notes': '.note-item, .feed-item',
            'titles': '.title, h3',
            'images': '.img, img'
        }
        
        # 测试小红书搜索
        return await self.test_platform(
            '小红书-漫剧搜索',
            'https://www.xiaohongshu.com/search_result?keyword=AI漫剧',
            selectors
        )
    
    async def test_douyin(self):
        """测试抖音"""
        selectors = {
            'videos': '.video-card, .feed-item',
            'titles': 'h3, .title',
            'user_info': '.user-info, .author'
        }
        
        # 测试抖音搜索
        return await self.test_platform(
            '抖音-短剧搜索',
            'https://www.douyin.com/search/AI%E6%BC%AB%E5%89%A7',
            selectors
        )
    
    async def test_kuaishou(self):
        """测试快手"""
        selectors = {
            'videos': '.video-item, .feed-item',
            'titles': '.title, h3',
            'authors': '.author-name'
        }
        
        return await self.test_platform(
            '快手-短剧',
            'https://www.kuaishou.com/short-play',
            selectors
        )
    
    async def test_wechat_channels(self):
        """测试微信视频号"""
        # 视频号主要在移动端，测试网页版
        return await self.test_platform(
            '微信视频号',
            'https://channels.weixin.qq.com/',
            {}
        )
    
    async def test_douban(self):
        """测试豆瓣（用于分析讨论）"""
        selectors = {
            'topics': '.topic-item, .post-item',
            'titles': '.title, h3',
            'discussions': '.comment, .reply'
        }
        
        return await self.test_platform(
            '豆瓣-短剧讨论',
            'https://www.douban.com/search?q=短剧',
            selectors
        )
    
    async def test_zhihu(self):
        """测试知乎（用于分析讨论）"""
        selectors = {
            'answers': '.ContentItem, .AnswerItem',
            'titles': '.ContentItem-title, h2',
            'votes': '.VoteButton'
        }
        
        return await self.test_platform(
            '知乎-AI漫剧讨论',
            'https://www.zhihu.com/search?type=content&q=AI漫剧',
            selectors
        )
    
    def generate_report(self):
        """生成测试报告"""
        print(f"\n{'='*60}")
        print("📊 平台权限测试报告")
        print(f"{'='*60}\n")
        
        accessible = [r for r in self.results if r['status'] == 'accessible']
        login_required = [r for r in self.results if r['status'] == 'login_required']
        anti_crawl = [r for r in self.results if r['status'] == 'anti_crawl']
        errors = [r for r in self.results if r['status'] == 'error']
        
        print(f"✅ 无需登录可访问: {len(accessible)}个平台")
        for r in accessible:
            print(f"   • {r['platform']}")
        
        print(f"\n🔐 需要登录: {len(login_required)}个平台")
        for r in login_required:
            print(f"   • {r['platform']}")
        
        print(f"\n🛡️ 有反爬机制: {len(anti_crawl)}个平台")
        for r in anti_crawl:
            print(f"   • {r['platform']}")
        
        print(f"\n❌ 访问错误: {len(errors)}个平台")
        for r in errors:
            print(f"   • {r['platform']}: {r['details'].get('error', 'Unknown')}")
        
        # 保存JSON报告
        report_path = self.test_dir / f"platform_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细报告已保存: {report_path}")
        
        return {
            'accessible': accessible,
            'login_required': login_required,
            'anti_crawl': anti_crawl,
            'errors': errors
        }


async def main():
    """主程序"""
    print("🧪 漫剧平台权限测试系统启动")
    print("="*60)
    print("\n⚠️  注意: 本次测试将打开浏览器窗口进行真实访问测试")
    print("     测试过程中请勿操作浏览器\n")
    
    async with PlatformTester() as tester:
        # 测试各平台
        print("\n📋 测试平台列表:")
        print("  1. B站短剧分区")
        print("  2. 小红书-漫剧搜索")
        print("  3. 抖音-短剧搜索")
        print("  4. 快手-短剧")
        print("  5. 微信视频号")
        print("  6. 豆瓣-短剧讨论")
        print("  7. 知乎-AI漫剧讨论")
        
        # 执行测试
        await tester.test_bilibili()
        await tester.test_xiaohongshu()
        await tester.test_douyin()
        await tester.test_kuaishou()
        await tester.test_wechat_channels()
        await tester.test_douban()
        await tester.test_zhihu()
        
        # 生成报告
        report = tester.generate_report()
    
    print("\n" + "="*60)
    print("✅ 平台测试完成！")
    print("="*60)
    
    # 输出需要用户协助的平台
    need_help = report['login_required'] + report['anti_crawl'] + report['errors']
    if need_help:
        print("\n⚠️  以下平台需要你的协助:")
        for r in need_help:
            print(f"   • {r['platform']}: {r['status']}")
    else:
        print("\n🎉 所有平台均可正常访问！")


if __name__ == '__main__':
    asyncio.run(main())
