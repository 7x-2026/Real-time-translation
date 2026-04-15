"""Whisper 语音转文字模块"""
import io
import numpy as np
import soundfile as sf
from openai import OpenAI
from config import config


class Transcriber:
    """Whisper 语音识别器"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url
        )
        self.model = config.whisper_model
        self.sample_rate = config.sample_rate
        
    def transcribe(self, audio_data: np.ndarray) -> str:
        """
        将音频数据转为文字
        
        Args:
            audio_data: numpy 音频数组
            
        Returns:
            识别出的文字
        """
        try:
            # 归一化音频数据到 [-1, 1] 范围
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            if np.max(np.abs(audio_data)) > 1.0:
                audio_data = audio_data / np.max(np.abs(audio_data))
            
            # 转换为 MP3 字节流
            buffer = io.BytesIO()
            sf.write(buffer, audio_data, self.sample_rate, format='WAV')
            buffer.seek(0)
            
            # 调用 Whisper API
            response = self.client.audio.transcriptions.create(
                model=self.model,
                file=("audio.wav", buffer.read()),
                language="en",
                response_format="text"
            )
            
            return response.strip() if response else ""
            
        except Exception as e:
            print(f"语音识别错误: {e}")
            return ""
    
    def transcribe_file(self, file_path: str) -> str:
        """转录音频文件"""
        try:
            with open(file_path, 'rb') as f:
                response = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=f,
                    language="en",
                    response_format="text"
                )
            return response.strip() if response else ""
        except Exception as e:
            print(f"文件转录错误: {e}")
            return ""