# 语音转录功能配置文档

## ✅ 安装状态

### 已安装的组件
1. **OpenAI Whisper** - 语音识别引擎
   - 版本: 20240930
   - 安装路径: `/Users/wangjingwen/Library/Python/3.9/lib/python/site-packages/whisper`
   - Python 版本: 3.9.6

2. **ffmpeg** - 音频处理工具
   - 版本: 8.0.1
   - 安装路径: `/opt/homebrew/Cellar/ffmpeg/8.0.1_4`

3. **依赖库**
   - torch (PyTorch) - 深度学习框架
   - numpy - 数值计算
   - tiktoken - 文本处理
   - numba - JIT编译加速

### 已下载模型
- **small** 模型 (461MB) - 适合中文语音识别
  - 路径: `~/.cache/whisper/small.pt`
  - 首次使用自动下载

---

## 📖 使用方法

### 方法1: 使用快捷脚本
```bash
cd /Users/wangjingwen/.openclaw/workspace
python3 voice_transcriber.py /path/to/audio.ogg
```

### 方法2: 使用完整功能脚本
```bash
cd /Users/wangjingwen/.openclaw/workspace
python3 transcribe.py /path/to/audio.ogg [模型大小] [语言]
```

示例:
```bash
# 使用 small 模型转录中文语音
python3 transcribe.py voice.ogg small zh

# 使用 tiny 模型（更快但精度稍低）
python3 transcribe.py voice.ogg tiny zh

# 使用 medium 模型（更慢但更准确）
python3 transcribe.py voice.ogg medium zh
```

### 方法3: 作为 Python 模块导入
```python
from voice_transcriber import quick_transcribe, transcribe_voice

# 快速转录
text = quick_transcribe("/path/to/audio.ogg")
print(text)

# 使用特定模型
text = transcribe_voice("/path/to/audio.ogg", model_name="medium")
```

### 方法4: 使用命令行工具 (whisper)
```bash
/Users/wangjingwen/Library/Python/3.9/bin/whisper audio.ogg --language Chinese --model small
```

---

## 🎯 支持的音频格式

- **.ogg** (Opus/Vorbis) - Telegram/飞书语音消息默认格式 ✅
- .mp3
- .wav
- .m4a
- .flac
- 以及其他 ffmpeg 支持的格式

---

## 🌐 支持的模型

| 模型 | 大小 | 速度 | 精度 | 推荐场景 |
|------|------|------|------|----------|
| tiny | 39 MB | 最快 | 较低 | 快速测试 |
| base | 74 MB | 快 | 一般 | 实时性要求高 |
| **small** | 461 MB | 中等 | 良好 | **推荐日常使用** |
| medium | 1.5 GB | 慢 | 很好 | 高精度需求 |
| large | 2.9 GB | 最慢 | 最佳 | 专业用途 |

---

## 🧪 测试结果

### 测试文件
- **文件**: `/Users/wangjingwen/.openclaw/media/inbound/718466b0-b639-4287-aef4-0fdf7d4d1c19.ogg`
- **格式**: Ogg Opus
- **大小**: 11,397 字节
- **模型**: small
- **语言**: 中文 (zh)

### 转录结果
```
测试一下 你现在可以听到我说话吗然后你给我说一下现在的交易情况吧
```

### 测试结论
✅ **成功** - 中文语音识别准确，标点自然

---

## 📁 文件说明

```
/Users/wangjingwen/.openclaw/workspace/
├── transcribe.py           # 完整功能脚本
├── voice_transcriber.py    # 简化接口（推荐集成使用）
└── VOICE_SETUP.md          # 本文档
```

---

## ⚠️ 注意事项

1. **首次使用** - 需要下载模型文件，根据模型大小可能需要 1-10 分钟
2. **硬件要求** - 推荐使用 M1/M2/M3 Mac，CPU 运行速度较慢
3. **内存占用** - small 模型约需 1GB 内存，large 模型约需 4GB+
4. **模型缓存** - 模型下载后保存在 `~/.cache/whisper/`，无需重复下载

---

## 🔧 故障排除

### 问题1: "ffmpeg not found"
**解决**: `brew install ffmpeg`

### 问题2: "No module named 'whisper'"
**解决**: `pip3 install openai-whisper`

### 问题3: 转录速度很慢
**解决**: 使用更小的模型 (tiny/base) 或检查是否在使用 GPU/MPS

### 问题4: 中文识别不准确
**解决**: 
- 确保指定了 `--language zh` 或 `language="zh"`
- 尝试使用更大的模型 (medium/large)
- 检查音频质量

---

## 📝 集成建议

对于飞书机器人语音消息转录，可以：

```python
import os
from voice_transcriber import quick_transcribe

# 语音消息处理函数
def handle_voice_message(file_path):
    if os.path.exists(file_path):
        text = quick_transcribe(file_path)
        return text
    return None
```
