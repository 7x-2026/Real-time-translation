"""音频捕获模块 - 使用 WASAPI loopback 捕获系统声音"""
import numpy as np
import soundcard as sc
import threading
import queue
from typing import Optional, Callable
from config import config


class AudioCapture:
    """系统音频捕获器"""
    
    def __init__(self):
        self.sample_rate = config.sample_rate
        self.channels = config.audio_channels
        self.chunk_samples = config.chunk_samples
        self.audio_queue = queue.Queue()
        self.is_running = False
        self.capture_thread: Optional[threading.Thread] = None
        self._loopback_mic = None
        
    def _get_loopback_mic(self):
        """获取系统音频回环麦克风"""
        try:
            # 在 Windows 上查找 WASAPI 回环设备
            mics = sc.all_microphones(include_loopback=True)
            for mic in mics:
                if hasattr(mic, 'isloopback') and mic.isloopback:
                    return mic
                # 尝试通过名称识别回环设备
                if 'loopback' in mic.name.lower() or '立体声混音' in mic.name:
                    return mic
            # 如果没找到特定回环设备，使用默认麦克风
            return sc.default_microphone()
        except Exception as e:
            print(f"获取音频设备失败: {e}")
            return None
    
    def start(self, callback: Optional[Callable[[np.ndarray], None]] = None):
        """开始捕获音频"""
        self._loopback_mic = self._get_loopback_mic()
        if not self._loopback_mic:
            raise RuntimeError("无法找到音频捕获设备")
        
        print(f"使用音频设备: {self._loopback_mic.name}")
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, args=(callback,))
        self.capture_thread.daemon = True
        self.capture_thread.start()
        
    def _capture_loop(self, callback: Optional[Callable[[np.ndarray], None]] = None):
        """音频捕获循环"""
        try:
            with self._loopback_mic.recorder(
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.chunk_samples
            ) as recorder:
                print("音频捕获已启动，正在监听系统声音...")
                while self.is_running:
                    # 录制音频块
                    data = recorder.record(numframes=self.chunk_samples)
                    if data is not None and len(data) > 0:
                        # 转换为单声道（如果需要）
                        if data.ndim > 1 and self.channels == 1:
                            data = data.mean(axis=1)
                        
                        # 放入队列
                        self.audio_queue.put(data)
                        
                        # 回调处理
                        if callback:
                            callback(data)
        except Exception as e:
            print(f"音频捕获错误: {e}")
            self.is_running = False
    
    def get_audio_chunk(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """从队列获取音频数据"""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def stop(self):
        """停止捕获"""
        self.is_running = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)
        # 清空队列
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        print("音频捕获已停止")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()