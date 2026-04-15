"""配置管理模块"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """应用配置"""
    # OpenAI 配置 (硅基流动)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1")
    
    # 模型配置
    whisper_model: str = os.getenv("WHISPER_MODEL", "FunAudioLLM/SenseVoiceSmall")
    # translation_model: str = os.getenv("TRANSLATION_MODEL", "deepseek-ai/DeepSeek-V2.5")
    translation_model: str = os.getenv("TRANSLATION_MODEL", "tencent/Hunyuan-MT-7B")
    
    # 音频配置
    sample_rate: int = int(os.getenv("SAMPLE_RATE", "16000"))
    chunk_duration: int = int(os.getenv("CHUNK_DURATION", "3"))
    audio_channels: int = int(os.getenv("AUDIO_CHANNELS", "1"))
    
    # 显示配置
    show_overlay: bool = os.getenv("SHOW_OVERLAY", "true").lower() == "true"
    overlay_opacity: float = float(os.getenv("OVERLAY_OPACITY", "0.85"))
    
    @property
    def chunk_samples(self) -> int:
        """计算每段音频样本数"""
        return self.sample_rate * self.chunk_duration
    
    def validate(self) -> bool:
        """验证配置是否有效"""
        if not self.openai_api_key:
            print("错误: 未设置 OPENAI_API_KEY")
            return False
        return True


# 全局配置实例
config = Config()
