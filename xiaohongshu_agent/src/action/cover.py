#!/usr/bin/env python3
"""
CoverGenerator - 封面生成器
"""

import os
import json
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger("xhs_agent.cover")


class CoverGenerator:
    """封面生成器 - 调用 cover-templates"""
    
    def __init__(self, config: dict):
        self.config = config
        self.template_dir = config.get('template_dir', '../cover-templates')
        self.output_dir = config.get('output_dir', 'data/covers')
        
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def render(self, template: str, params: dict) -> str:
        """渲染封面"""
        import sys
        sys.path.insert(0, self.template_dir)
        
        try:
            from render_cover import CoverRenderer
            
            renderer = CoverRenderer(output_dir=self.output_dir)
            
            # 构建参数
            cover_params = {
                "title": params.get("title", ""),
                "subtitle": params.get("subtitle", ""),
                "serial_number": params.get("serial_number", "01"),
                "tag_text": params.get("tag_text", "#王小橙的观察日记 🤖"),
                "avatar_emoji": params.get("avatar_emoji", "🍊"),
            }
            
            # 特定模板参数
            if template == "blue_knowledge":
                cover_params["number_badge"] = params.get("number_badge", "")
            elif template == "cyber_neon":
                cover_params["terminal_line"] = params.get("terminal_line", "")
                cover_params["code_tag"] = params.get("code_tag", "")
            elif template == "warm_persona":
                cover_params["emoji_big"] = params.get("emoji_big", "")
                cover_params["pill_tags"] = params.get("pill_tags", [])
            elif template == "versus_split":
                cover_params["top_text"] = params.get("top_text", "")
                cover_params["top_label"] = params.get("top_label", "")
                cover_params["bottom_text"] = params.get("bottom_text", "")
                cover_params["bottom_label"] = params.get("bottom_label", "")
                cover_params["vs_text"] = params.get("vs_text", "VS")
            
            path = renderer.render(template, cover_params)
            logger.info(f"封面生成: {path}")
            return path
            
        except Exception as e:
            logger.error(f"封面生成失败: {e}")
            return ""
    
    def select_template(self, note_type: str) -> str:
        """根据笔记类型选择模板"""
        mapping = {
            "daily_observation": "orange_impact",
            "trending": "orange_impact",
            "tutorial": "blue_knowledge",
            "tools": "blue_knowledge",
            "deep_thought": "minimal_white",
            "opinion": "minimal_white",
            "ai_tech": "cyber_neon",
            "coding": "cyber_neon",
            "persona": "warm_persona",
            "series": "warm_persona",
            "comparison": "versus_split",
            "vote": "versus_split",
        }
        return mapping.get(note_type, "orange_impact")
