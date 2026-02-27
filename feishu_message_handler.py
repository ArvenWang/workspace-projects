#!/usr/bin/env python3
"""
飞书机器人消息处理器
处理文本、图片、语音消息，集成所有现有能力
"""

import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

# 添加 workspace 到路径
WORKSPACE = Path("/Users/wangjingwen/.openclaw/workspace")
sys.path.insert(0, str(WORKSPACE))

# 尝试导入语音转录模块
try:
    from voice_transcriber import quick_transcribe
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️ 语音转录模块未安装，语音功能将不可用")


class FeishuMessageHandler:
    """飞书消息处理器"""
    
    def __init__(self):
        self.workspace = WORKSPACE
        self.temp_dir = Path(tempfile.gettempdir()) / "feishu_bot"
        self.temp_dir.mkdir(exist_ok=True)
        
    def handle_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理飞书消息
        
        Args:
            message_data: 飞书消息数据
            
        Returns:
            处理结果
        """
        msg_type = message_data.get("msg_type", "text")
        content = message_data.get("content", {})
        
        # 根据消息类型处理
        if msg_type == "text":
            return self._handle_text(content)
        elif msg_type == "image":
            return self._handle_image(content, message_data)
        elif msg_type == "audio":
            return self._handle_audio(content, message_data)
        elif msg_type == "file":
            return self._handle_file(content, message_data)
        else:
            return {
                "type": "text",
                "content": f"暂不支持的消息类型: {msg_type}"
            }
    
    def _handle_text(self, content: Dict) -> Dict[str, Any]:
        """处理文本消息"""
        text = content.get("text", "")
        return {
            "type": "text",
            "content": text,
            "processed": True
        }
    
    def _handle_image(self, content: Dict, full_data: Dict) -> Dict[str, Any]:
        """处理图片消息"""
        image_key = content.get("image_key", "")
        
        # 下载图片（需要飞书 API）
        image_path = self._download_image(image_key)
        
        if image_path and image_path.exists():
            return {
                "type": "image",
                "image_key": image_key,
                "local_path": str(image_path),
                "description": "图片已下载，可以进行视觉分析"
            }
        else:
            return {
                "type": "text",
                "content": "📷 收到图片，但下载失败"
            }
    
    def _handle_audio(self, content: Dict, full_data: Dict) -> Dict[str, Any]:
        """处理语音消息"""
        if not WHISPER_AVAILABLE:
            return {
                "type": "text",
                "content": "🎤 收到语音消息，但语音转文字功能未启用"
            }
        
        file_key = content.get("file_key", "")
        
        # 下载语音文件
        audio_path = self._download_audio(file_key)
        
        if audio_path and audio_path.exists():
            try:
                # 转录语音
                transcript = quick_transcribe(str(audio_path))
                
                return {
                    "type": "audio_transcript",
                    "file_key": file_key,
                    "local_path": str(audio_path),
                    "transcript": transcript,
                    "original_duration": content.get("duration", 0)
                }
            except Exception as e:
                return {
                    "type": "text",
                    "content": f"🎤 语音转文字失败: {str(e)}"
                }
        else:
            return {
                "type": "text",
                "content": "🎤 收到语音消息，但下载失败"
            }
    
    def _handle_file(self, content: Dict, full_data: Dict) -> Dict[str, Any]:
        """处理文件消息"""
        file_key = content.get("file_key", "")
        file_name = content.get("file_name", "unknown")
        
        return {
            "type": "file",
            "file_key": file_key,
            "file_name": file_name,
            "description": f"收到文件: {file_name}"
        }
    
    def _download_image(self, image_key: str) -> Optional[Path]:
        """下载图片"""
        # 这里需要调用飞书 API 下载图片
        # 实际实现需要集成飞书 SDK
        # 返回本地文件路径
        return None
    
    def _download_audio(self, file_key: str) -> Optional[Path]:
        """下载语音文件"""
        # 这里需要调用飞书 API 下载语音
        # 实际实现需要集成飞书 SDK
        # 返回本地文件路径
        return None


def process_inbound_message(message_json: str) -> str:
    """
    处理入站消息的入口函数
    
    Args:
        message_json: JSON 格式的飞书消息
        
    Returns:
        JSON 格式的处理结果
    """
    try:
        message_data = json.loads(message_json)
        handler = FeishuMessageHandler()
        result = handler.handle_message(message_data)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "type": "error",
            "error": str(e)
        }, ensure_ascii=False)


# 命令行测试
if __name__ == "__main__":
    # 测试文本消息
    test_text = json.dumps({
        "msg_type": "text",
        "content": {"text": "你好，测试一下"}
    })
    
    print("测试文本消息处理:")
    print(process_inbound_message(test_text))
    print()
    
    # 测试语音消息
    test_audio = json.dumps({
        "msg_type": "audio",
        "content": {
            "file_key": "file_xxx",
            "duration": 5000
        }
    })
    
    print("测试语音消息处理:")
    print(process_inbound_message(test_audio))
