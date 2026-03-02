#!/usr/bin/env python3
"""
语音转录工具 - 使用 OpenAI Whisper 转录语音消息为文字
支持 .ogg 格式，针对中文语音识别优化
"""

import sys
import os
import whisper
import tempfile
import subprocess

# 默认模型，small 支持中文且速度适中
DEFAULT_MODEL = "small"

def check_ffmpeg():
    """检查 ffmpeg 是否安装"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def transcribe_audio(file_path, model_size=DEFAULT_MODEL, language="zh"):
    """
    转录音频文件
    
    Args:
        file_path: 音频文件路径
        model_size: 模型大小 (tiny, base, small, medium, large)
        language: 语言代码，zh 表示中文
    
    Returns:
        转录的文本
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"音频文件不存在: {file_path}")
    
    # 检查 ffmpeg
    if not check_ffmpeg():
        print("警告: ffmpeg 未安装。正在尝试安装...")
        install_ffmpeg()
    
    # 加载模型
    print(f"正在加载 Whisper 模型: {model_size}...")
    model = whisper.load_model(model_size)
    
    # 转录音频
    print(f"正在转录音频: {file_path}")
    result = model.transcribe(
        file_path,
        language=language,
        task="transcribe"
    )
    
    return result["text"].strip()

def install_ffmpeg():
    """尝试安装 ffmpeg"""
    try:
        # 检查是否安装了 homebrew
        subprocess.run(['brew', '--version'], capture_output=True, check=True)
        print("正在通过 Homebrew 安装 ffmpeg...")
        subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
        print("ffmpeg 安装成功！")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 无法自动安装 ffmpeg。请手动安装:")
        print("  brew install ffmpeg")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("用法: python3 transcribe.py <音频文件路径> [模型大小] [语言代码]")
        print("示例: python3 transcribe.py voice.ogg small zh")
        print("\n支持的模型大小: tiny, base, small, medium, large")
        print("语言代码: zh (中文), en (英文), ja (日文), 等")
        sys.exit(1)
    
    file_path = sys.argv[1]
    model_size = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MODEL
    language = sys.argv[3] if len(sys.argv) > 3 else "zh"
    
    try:
        text = transcribe_audio(file_path, model_size, language)
        print("\n" + "="*50)
        print("转录结果:")
        print("="*50)
        print(text)
        print("="*50)
    except Exception as e:
        print(f"转录失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
