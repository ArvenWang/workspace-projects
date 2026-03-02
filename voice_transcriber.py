#!/usr/bin/env python3
"""
语音消息转录工具 - 简化接口
自动下载模型，支持中文语音识别
"""

import os
import sys
import whisper

# 默认模型路径
MODEL_CACHE_DIR = os.path.expanduser("~/.openclaw/whisper_models")

def transcribe_voice(file_path, model_name="small"):
    """
    转录语音文件为文字
    
    Args:
        file_path: .ogg 或其他格式的音频文件路径
        model_name: 模型名称 (tiny, base, small, medium, large)
                   tiny 最快但精度最低，large 最慢但最准
    
    Returns:
        str: 转录的文本（中文）
    
    Raises:
        FileNotFoundError: 文件不存在
        Exception: 其他错误
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"音频文件不存在: {file_path}")
    
    # 加载模型（首次会自动下载）
    model = whisper.load_model(model_name)
    
    # 转录，指定中文
    result = model.transcribe(file_path, language="zh", task="transcribe")
    
    return result["text"].strip()

def quick_transcribe(file_path):
    """
    快速转录（使用 small 模型，平衡速度和精度）
    
    Args:
        file_path: 音频文件路径
    
    Returns:
        str: 转录的文本
    """
    return transcribe_voice(file_path, model_name="small")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 voice_transcriber.py <音频文件路径>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    try:
        text = quick_transcribe(file_path)
        print(text)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
