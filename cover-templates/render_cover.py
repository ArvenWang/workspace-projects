#!/usr/bin/env python3
"""
小红书封面渲染器 - OpenClaw AI 专用 v2
======================================
通过 Playwright 无头浏览器将 HTML 模板渲染为 1080x1440 的封面图片。
v2: 6套模板 + 字体自适应 + 统一序号

使用方式:
  1. 命令行:
     python render_cover.py --template orange_impact --title "标题" --output cover.jpg

  2. Python:
     from render_cover import CoverRenderer
     renderer = CoverRenderer()
     path = renderer.render("orange_impact", {"title": "...", "serial_number": "01"})

  3. JSON:
     python render_cover.py --json '{"template":"orange_impact","params":{"title":"xxx","serial_number":"01"}}'

依赖: pip install playwright && playwright install chromium
"""

import json
import time
import re
import argparse
import logging
from pathlib import Path
from string import Template

logger = logging.getLogger("cover_renderer")

# ─── 字体自适应 JS ───

ADAPTIVE_FONT_JS = """
(function() {
  document.querySelectorAll('[data-adaptive-title]').forEach(function(el) {
    var text = el.textContent.replace(/\\s+/g, '');
    var len = text.length;
    var size;
    if (len <= 8) size = 110;
    else if (len <= 12) size = 96;
    else if (len <= 18) size = 84;
    else if (len <= 24) size = 72;
    else if (len <= 32) size = 64;
    else size = 56;
    el.style.fontSize = size + 'px';
  });
  document.querySelectorAll('[data-adaptive-split]').forEach(function(el) {
    var text = el.textContent.replace(/\\s+/g, '');
    var len = text.length;
    var size;
    if (len <= 6) size = 96;
    else if (len <= 10) size = 80;
    else size = 64;
    el.style.fontSize = size + 'px';
  });
})();
"""

# ─── HTML 片段模板 ───

TEMPLATE_FRAGMENTS = {
    "orange_impact": Template("""
<div class="cover orange-impact" id="cover-canvas">
  <div class="serial-number">${serial_number}</div>
  <div class="title" data-adaptive-title>${title}</div>
  <div class="subtitle">${subtitle}</div>
  <div class="tag">
    <span class="tag-text">${tag_text}</span>
    <div class="tag-avatar">${avatar_emoji}</div>
  </div>
</div>
"""),

    "blue_knowledge": Template("""
<div class="cover blue-knowledge" id="cover-canvas">
  <div class="serial-number">${serial_number}</div>
  <div class="card">
    <div class="card-accent"></div>
    <div class="number-badge">${number_badge}</div>
    <div class="title" data-adaptive-title>${title}</div>
    <div class="subtitle">${subtitle}</div>
  </div>
  <div class="tag">
    <span class="tag-text">${tag_text}</span>
    <div class="tag-avatar">${avatar_emoji}</div>
  </div>
</div>
"""),

    "minimal_white": Template("""
<div class="cover minimal-white" id="cover-canvas">
  <div class="serial-number">${serial_number}</div>
  <div class="corner-decor top-right"></div>
  <div class="corner-decor bottom-left"></div>
  <div class="content-area">
    <div class="accent-line"></div>
    <div class="title" data-adaptive-title>${title}</div>
    <div class="subtitle">${subtitle}</div>
  </div>
  <div class="tag">
    <span class="tag-text">${tag_text}</span>
    <div class="tag-avatar">${avatar_emoji}</div>
  </div>
</div>
"""),

    "cyber_neon": Template("""
<div class="cover cyber-neon" id="cover-canvas">
  <div class="serial-number">${serial_number}</div>
  <div class="bg-grid"></div>
  <div class="glow-orb green"></div>
  <div class="glow-orb purple"></div>
  <div class="terminal-line">${terminal_line}</div>
  <div class="title" data-adaptive-title>${title}</div>
  <div class="subtitle">${subtitle}</div>
  <div class="code-tag">&lt;code&gt; ${code_tag} &lt;/code&gt;</div>
  <div class="tag">
    <span class="tag-text">${tag_text}</span>
    <div class="tag-avatar">${avatar_emoji}</div>
  </div>
</div>
"""),

    "warm_persona": Template("""
<div class="cover warm-persona" id="cover-canvas">
  <div class="serial-number">${serial_number}</div>
  <div class="deco-blob a"></div>
  <div class="deco-blob b"></div>
  <div class="content-area">
    <div class="emoji-big">${emoji_big}</div>
    <div class="title" data-adaptive-title>${title}</div>
    <div class="subtitle">${subtitle}</div>
    <div class="pill-tags">${pill_tags_html}</div>
  </div>
  <div class="tag">
    <span class="tag-text">${tag_text}</span>
    <div class="tag-avatar">${avatar_emoji}</div>
  </div>
</div>
"""),

    "versus_split": Template("""
<div class="cover versus-split" id="cover-canvas">
  <div class="serial-number">${serial_number}</div>
  <div class="split-top">
    <div class="split-text" data-adaptive-split>${top_text}</div>
    <div class="split-label">${top_label}</div>
  </div>
  <div class="split-bottom">
    <div class="split-text" data-adaptive-split>${bottom_text}</div>
    <div class="split-label">${bottom_label}</div>
  </div>
  <div class="vs-badge">${vs_text}</div>
  <div class="tag">
    <span class="tag-text">${tag_text}</span>
  </div>
</div>
"""),
}

# ─── 默认参数 ───

DEFAULTS = {
    "title": "",
    "subtitle": "",
    "serial_number": "",
    "number_badge": "",
    "terminal_line": "",
    "code_tag": "",
    "emoji_big": "🤖",
    "top_text": "",
    "bottom_text": "",
    "top_label": "",
    "bottom_label": "",
    "vs_text": "VS",
    "tag_text": "#王小橙的观察日记 🤖",
    "avatar_emoji": "🍊",
    "pill_tags": [],
}

# ─── CSS 样式 ───

PAGE_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: transparent; }
.cover {
  width: 1080px; height: 1440px; position: relative; overflow: hidden;
  font-family: "PingFang SC","Noto Sans SC","Microsoft YaHei",sans-serif;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
}
.cover .serial-number {
  position: absolute; top: 70px; right: 70px; font-size: 200px; font-weight: 900;
  line-height: 1; z-index: 1; opacity: 0.1; color: inherit;
}

/* orange_impact */
.cover.orange-impact { background: linear-gradient(135deg, #FF6B35 0%, #F7931E 50%, #FFB347 100%); }
.cover.orange-impact::before { content:''; position:absolute; top:-200px; right:-200px; width:600px; height:600px; border-radius:50%; background:rgba(255,255,255,0.08); }
.cover.orange-impact::after { content:''; position:absolute; bottom:-150px; left:-150px; width:500px; height:500px; border-radius:50%; background:rgba(255,255,255,0.06); }
.cover.orange-impact .serial-number { color:#FFF; }
.cover.orange-impact .title { color:#FFF; font-weight:900; line-height:1.25; text-align:center; padding:0 72px; text-shadow:0 4px 20px rgba(0,0,0,0.15); position:relative; z-index:2; }
.cover.orange-impact .subtitle { color:rgba(255,255,255,0.85); font-size:44px; font-weight:500; margin-top:44px; text-align:center; padding:0 90px; position:relative; z-index:2; }
.cover.orange-impact .tag { position:absolute; bottom:60px; left:60px; right:60px; display:flex; justify-content:space-between; align-items:center; z-index:2; }
.cover.orange-impact .tag-text { color:rgba(255,255,255,0.7); font-size:32px; }
.cover.orange-impact .tag-avatar { width:68px; height:68px; border-radius:50%; background:rgba(255,255,255,0.2); display:flex; align-items:center; justify-content:center; font-size:38px; }

/* blue_knowledge */
.cover.blue-knowledge { background:#0F1923; }
.cover.blue-knowledge .serial-number { color:#FFF; }
.cover.blue-knowledge .card { width:920px; background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:28px; padding:72px 64px; position:relative; z-index:2; }
.cover.blue-knowledge .card-accent { width:64px; height:6px; background:#4A9EFF; border-radius:3px; margin-bottom:40px; }
.cover.blue-knowledge .title { color:#FFF; font-weight:800; line-height:1.3; text-align:left; }
.cover.blue-knowledge .subtitle { color:rgba(255,255,255,0.5); font-size:40px; font-weight:400; margin-top:36px; text-align:left; line-height:1.5; }
.cover.blue-knowledge .number-badge { display:inline-flex; align-items:center; background:#4A9EFF; color:#FFF; font-size:40px; font-weight:800; padding:14px 36px; border-radius:14px; margin-bottom:36px; }
.cover.blue-knowledge .tag { position:absolute; bottom:60px; left:60px; right:60px; display:flex; justify-content:space-between; align-items:center; z-index:2; }
.cover.blue-knowledge .tag-text { color:rgba(255,255,255,0.35); font-size:30px; }
.cover.blue-knowledge .tag-avatar { width:68px; height:68px; border-radius:50%; background:rgba(255,255,255,0.08); display:flex; align-items:center; justify-content:center; font-size:38px; }

/* minimal_white */
.cover.minimal-white { background:#FAFAF8; }
.cover.minimal-white .serial-number { color:#1A1A1A; }
.cover.minimal-white .content-area { padding:0 90px; width:100%; position:relative; z-index:2; }
.cover.minimal-white .accent-line { width:80px; height:6px; background:#1A1A1A; margin-bottom:48px; }
.cover.minimal-white .title { color:#1A1A1A; font-weight:800; line-height:1.35; text-align:left; letter-spacing:2px; }
.cover.minimal-white .subtitle { color:#999; font-size:42px; font-weight:400; margin-top:40px; text-align:left; line-height:1.6; }
.cover.minimal-white .tag { position:absolute; bottom:60px; left:90px; right:90px; display:flex; justify-content:space-between; align-items:center; z-index:2; }
.cover.minimal-white .tag-text { color:#CCC; font-size:28px; letter-spacing:1px; }
.cover.minimal-white .tag-avatar { width:68px; height:68px; border-radius:50%; background:#F0F0F0; display:flex; align-items:center; justify-content:center; font-size:38px; }
.cover.minimal-white .corner-decor { position:absolute; width:180px; height:180px; border:1px solid #E8E8E8; }
.cover.minimal-white .corner-decor.top-right { top:60px; right:60px; border-left:none; border-bottom:none; }
.cover.minimal-white .corner-decor.bottom-left { bottom:120px; left:60px; border-right:none; border-top:none; }

/* cyber_neon */
.cover.cyber-neon { background:#0D0D1A; }
.cover.cyber-neon .serial-number { color:#00FF88; }
.cover.cyber-neon .bg-grid { position:absolute; top:0; left:0; width:100%; height:100%; background-image:linear-gradient(rgba(0,255,136,0.04) 1px,transparent 1px),linear-gradient(90deg,rgba(0,255,136,0.04) 1px,transparent 1px); background-size:60px 60px; z-index:1; }
.cover.cyber-neon .glow-orb { position:absolute; border-radius:50%; filter:blur(120px); z-index:1; }
.cover.cyber-neon .glow-orb.green { width:400px; height:400px; background:rgba(0,255,136,0.15); top:200px; right:-100px; }
.cover.cyber-neon .glow-orb.purple { width:350px; height:350px; background:rgba(123,104,238,0.12); bottom:200px; left:-80px; }
.cover.cyber-neon .title { color:#00FF88; font-weight:900; line-height:1.25; text-align:center; padding:0 72px; text-shadow:0 0 40px rgba(0,255,136,0.3),0 0 80px rgba(0,255,136,0.1); position:relative; z-index:2; }
.cover.cyber-neon .subtitle { color:rgba(255,255,255,0.5); font-size:42px; font-weight:400; margin-top:40px; text-align:center; padding:0 90px; position:relative; z-index:2; }
.cover.cyber-neon .code-tag { display:inline-block; background:rgba(0,255,136,0.1); border:1px solid rgba(0,255,136,0.3); color:#00FF88; font-size:32px; font-family:"SF Mono","Fira Code","Consolas",monospace; padding:14px 32px; border-radius:8px; margin-top:44px; position:relative; z-index:2; }
.cover.cyber-neon .tag { position:absolute; bottom:60px; left:60px; right:60px; display:flex; justify-content:space-between; align-items:center; z-index:2; }
.cover.cyber-neon .tag-text { color:rgba(255,255,255,0.3); font-size:30px; font-family:"SF Mono","Fira Code","Consolas",monospace; }
.cover.cyber-neon .tag-avatar { width:68px; height:68px; border-radius:50%; background:rgba(0,255,136,0.1); border:1px solid rgba(0,255,136,0.3); display:flex; align-items:center; justify-content:center; font-size:38px; }
.cover.cyber-neon .terminal-line { position:absolute; top:80px; left:80px; color:rgba(0,255,136,0.2); font-size:28px; font-family:"SF Mono","Fira Code","Consolas",monospace; z-index:2; }

/* warm_persona */
.cover.warm-persona { background:linear-gradient(160deg,#FFE5E5 0%,#FFF0E5 30%,#FFF8E8 60%,#FFFDF5 100%); }
.cover.warm-persona .serial-number { color:#FF6B35; }
.cover.warm-persona .deco-blob { position:absolute; border-radius:50%; z-index:1; }
.cover.warm-persona .deco-blob.a { width:500px; height:500px; background:rgba(255,107,107,0.08); top:-100px; left:-100px; }
.cover.warm-persona .deco-blob.b { width:400px; height:400px; background:rgba(255,165,0,0.06); bottom:-80px; right:-80px; }
.cover.warm-persona .content-area { text-align:center; padding:0 72px; position:relative; z-index:2; }
.cover.warm-persona .emoji-big { font-size:140px; margin-bottom:48px; }
.cover.warm-persona .title { color:#2D2D2D; font-weight:800; line-height:1.3; }
.cover.warm-persona .subtitle { color:#888; font-size:42px; font-weight:400; margin-top:36px; line-height:1.5; }
.cover.warm-persona .pill-tags { display:flex; justify-content:center; gap:16px; margin-top:48px; flex-wrap:wrap; }
.cover.warm-persona .pill { background:rgba(255,107,53,0.1); color:#FF6B35; font-size:32px; font-weight:600; padding:14px 32px; border-radius:100px; }
.cover.warm-persona .tag { position:absolute; bottom:60px; left:60px; right:60px; display:flex; justify-content:space-between; align-items:center; z-index:2; }
.cover.warm-persona .tag-text { color:#CCC; font-size:30px; }
.cover.warm-persona .tag-avatar { width:68px; height:68px; border-radius:50%; background:rgba(255,107,53,0.1); display:flex; align-items:center; justify-content:center; font-size:38px; }

/* versus_split */
.cover.versus-split { background:#F5F5F3; flex-direction:column; justify-content:stretch; }
.cover.versus-split .serial-number { color:#1A1A1A; z-index:5; }
.cover.versus-split .split-top { width:100%; height:50%; background:#FF6B35; display:flex; flex-direction:column; justify-content:center; align-items:center; padding:60px 80px; position:relative; z-index:2; }
.cover.versus-split .split-bottom { width:100%; height:50%; background:#1A1A1A; display:flex; flex-direction:column; justify-content:center; align-items:center; padding:60px 80px; position:relative; z-index:2; }
.cover.versus-split .split-text { color:#FFF; font-weight:900; text-align:center; line-height:1.3; }
.cover.versus-split .split-label { color:rgba(255,255,255,0.5); font-size:36px; font-weight:400; margin-top:20px; }
.cover.versus-split .vs-badge { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:130px; height:130px; border-radius:50%; background:#FFF; color:#1A1A1A; font-size:52px; font-weight:900; display:flex; align-items:center; justify-content:center; z-index:10; box-shadow:0 8px 40px rgba(0,0,0,0.15); }
.cover.versus-split .tag { position:absolute; bottom:40px; left:60px; right:60px; display:flex; justify-content:center; z-index:10; }
.cover.versus-split .tag-text { color:rgba(255,255,255,0.45); font-size:32px; }
"""

PAGE_SHELL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
__PAGE_CSS__
</style>
</head>
<body>
__COVER_HTML__
<script>
__ADAPTIVE_JS__
</script>
</body>
</html>"""


class CoverRenderer:
    """封面渲染器：HTML 模板 → Playwright 截图 → JPEG/PNG 图片"""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _build_params(self, template_name: str, params: dict) -> dict:
        """合并默认值，处理特殊字段"""
        merged = {**DEFAULTS, **params}

        # warm_persona: pill_tags 列表 → HTML
        if template_name == "warm_persona":
            pills = merged.get("pill_tags", [])
            if isinstance(pills, list):
                merged["pill_tags_html"] = "".join(
                    f'<span class="pill">{p}</span>' for p in pills
                )
            else:
                merged["pill_tags_html"] = ""

        return merged

    def _build_html(self, template_name: str, params: dict) -> str:
        """生成完整 HTML 页面"""
        if template_name not in TEMPLATE_FRAGMENTS:
            raise ValueError(f"未知模板: {template_name}，可选: {list(TEMPLATE_FRAGMENTS.keys())}")

        merged = self._build_params(template_name, params)
        fragment = TEMPLATE_FRAGMENTS[template_name].safe_substitute(merged)
        return (PAGE_SHELL
                .replace("__PAGE_CSS__", PAGE_CSS)
                .replace("__COVER_HTML__", fragment)
                .replace("__ADAPTIVE_JS__", ADAPTIVE_FONT_JS))

    def render(
        self,
        template_name: str,
        params: dict,
        output_filename: str = "",
        fmt: str = "jpeg",
        quality: int = 95,
    ) -> str:
        """
        渲染封面并导出为图片。

        Args:
            template_name: 模板名，如 "orange_impact"
            params: 模板参数字典，参见 cover_config.json
            output_filename: 输出文件名（不含扩展名），留空自动生成
            fmt: 导出格式 "jpeg" | "png"
            quality: JPEG 质量 (1-100)

        Returns:
            输出文件的绝对路径
        """
        from playwright.sync_api import sync_playwright

        html = self._build_html(template_name, params)

        if not output_filename:
            output_filename = f"cover_{template_name}_{int(time.time())}"

        ext = "jpg" if fmt == "jpeg" else "png"
        output_path = self.output_dir / f"{output_filename}.{ext}"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1080, "height": 1440})
            page.set_content(html, wait_until="networkidle")
            # 等待字体渲染 + JS 自适应执行
            page.wait_for_timeout(800)

            element = page.locator("#cover-canvas")
            screenshot_opts = {"path": str(output_path), "type": fmt}
            if fmt == "jpeg":
                screenshot_opts["quality"] = quality
            element.screenshot(**screenshot_opts)

            browser.close()

        logger.info(f"封面已生成: {output_path}")
        return str(output_path.resolve())

    def render_all_examples(self) -> list[str]:
        """渲染所有模板的示例封面"""
        config_path = Path(__file__).parent / "cover_config.json"
        with open(config_path) as f:
            config = json.load(f)

        paths = []
        for tpl_name, tpl_info in config["templates"].items():
            example = tpl_info.get("example", {})
            path = self.render(tpl_name, example, output_filename=f"example_{tpl_name}")
            paths.append(path)
            logger.info(f"  ✓ {tpl_name}: {path}")

        return paths

    def select_template(self, note_type: str) -> str:
        """根据笔记类型自动选择模板"""
        config_path = Path(__file__).parent / "cover_config.json"
        with open(config_path) as f:
            config = json.load(f)
        mapping = config["template_selection_guide"]["mapping"]
        return mapping.get(note_type, "orange_impact")


def main():
    parser = argparse.ArgumentParser(description="小红书封面渲染器 - OpenClaw AI 专用 v2")
    parser.add_argument("--template", "-t", type=str, help="模板名称")
    parser.add_argument("--title", type=str, default="", help="主标题")
    parser.add_argument("--subtitle", type=str, default="", help="副标题")
    parser.add_argument("--serial", type=str, default="", help="序号，如01/02")
    parser.add_argument("--output", "-o", type=str, default="", help="输出文件名")
    parser.add_argument("--format", type=str, default="jpeg", choices=["jpeg", "png"])
    parser.add_argument("--quality", type=int, default=95, help="JPEG质量")
    parser.add_argument("--json", type=str, default="", help="JSON参数（完整控制）")
    parser.add_argument("--output-dir", type=str, default="output", help="输出目录")
    parser.add_argument("--examples", action="store_true", help="渲染所有示例封面")
    parser.add_argument("--list", action="store_true", help="列出所有可用模板")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    renderer = CoverRenderer(output_dir=args.output_dir)

    if args.list:
        config_path = Path(__file__).parent / "cover_config.json"
        with open(config_path) as f:
            config = json.load(f)
        print("\n可用模板:")
        print("-" * 60)
        for name, info in config["templates"].items():
            print(f"  {name:20s}  {info['name']}  适用: {', '.join(info['use_cases'])}")
        print()
        return

    if args.examples:
        print("渲染所有示例封面...\n")
        paths = renderer.render_all_examples()
        print(f"\n完成! 共生成 {len(paths)} 张封面")
        return

    if args.json:
        data = json.loads(args.json)
        template = data.get("template", "orange_impact")
        params = data.get("params", {})
    elif args.template:
        template = args.template
        params = {}
        if args.title:
            params["title"] = args.title
        if args.subtitle:
            params["subtitle"] = args.subtitle
        if args.serial:
            params["serial_number"] = args.serial
    else:
        parser.print_help()
        return

    path = renderer.render(
        template_name=template,
        params=params,
        output_filename=args.output,
        fmt=args.format,
        quality=args.quality,
    )
    print(f"封面已生成: {path}")


if __name__ == "__main__":
    main()
