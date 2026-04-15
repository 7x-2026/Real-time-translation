# 🎙️ 实时英语翻译器

实时捕获 Windows 系统音频，通过 OpenAI Whisper 识别英文，再由 GPT 翻译成中文。

## 功能特性

- 🎵 **系统音频捕获**：无需麦克风，直接监听电脑播放的声音
- 🗣️ **语音识别**：FunAudioLLM/SenseVoiceSmall 阿里轻量化模型英文识别
- 🌐 **实时翻译**：tencent/Hunyuan-MT-7B 翻译模型快速中英翻译
- 💬 **悬浮字幕**：透明置顶窗口，原文译文双语显示
- 📟 **控制台输出**：Rich 美化界面，彩色区分
- 📄 **文件记录**：自动保存翻译历史

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

编辑 `.env` 文件：

```env
OPENAI_API_KEY=sk-your-key-here
```

### 3. 运行程序

双击 `start.bat` 或在 PowerShell 中运行：

```bash
python main.py
```

## 快捷键

- `Ctrl+C`：停止程序

## 悬浮窗口操作

- **拖动**：鼠标左键按住拖动位置
- **关闭**：右键菜单或关闭主程序

## 文件说明

- `main.py` - 主程序入口
- `config.py` - 配置管理
- `audio_capture.py` - 音频捕获模块
- `transcriber.py` - Whisper 语音识别
- `translator.py` - GPT 翻译模块
- `display/` - 显示模块（控制台/悬浮窗/日志）
- `translation_log.txt` - 翻译记录（自动创建）