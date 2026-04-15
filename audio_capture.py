"""音频捕获模块 - 使用 WASAPI loopback 捕获系统声音"""
import warnings
import numpy as np
import soundcard as sc
import threading
import queue
from typing import Optional, Callable
from config import config

warnings.filterwarnings("ignore", message="data discontinuity in recording")


class AudioCapture:
    """系统音频捕获器"""

    def __init__(self):
        self.sample_rate = config.sample_rate
        self.channels = config.audio_channels

        # 业务识别窗口：例如 3 秒
        self.target_chunk_samples = config.chunk_samples

        # 底层录音块：0.2 秒，保证稳定
        self.internal_block_samples = int(self.sample_rate * 0.2)

        # 最短送识别长度：2.5 秒
        self.min_commit_samples = int(self.sample_rate * 2.5)

        # 最长送识别长度：5 秒，避免无限堆积
        self.max_commit_samples = int(self.sample_rate * 5.0)

        # 静音判定参数
        self.silence_threshold = 0.003
        self.silence_blocks_to_commit = 3  # 连续约 0.6 秒静音则提交

        self.audio_queue = queue.Queue(maxsize=6)
        self.is_running = False
        self.capture_thread: Optional[threading.Thread] = None
        self._loopback_mic = None

    def _get_loopback_mic(self):
        try:
            mics = sc.all_microphones(include_loopback=True)
            for mic in mics:
                if hasattr(mic, "isloopback") and mic.isloopback:
                    return mic
                if "loopback" in mic.name.lower() or "立体声混音" in mic.name:
                    return mic
            return sc.default_microphone()
        except Exception as e:
            print(f"获取音频设备失败: {e}")
            return None

    def start(self, callback: Optional[Callable[[np.ndarray], None]] = None):
        self._loopback_mic = self._get_loopback_mic()
        if not self._loopback_mic:
            raise RuntimeError("无法找到音频捕获设备")

        print(f"使用音频设备: {self._loopback_mic.name}")
        self.is_running = True
        self.capture_thread = threading.Thread(
            target=self._capture_loop,
            args=(callback,),
            daemon=True
        )
        self.capture_thread.start()

    def _is_silent(self, data: np.ndarray) -> bool:
        if data.size == 0:
            return True
        rms = np.sqrt(np.mean(np.square(data.astype(np.float32))))
        return rms < self.silence_threshold

    def _enqueue_chunk(self, chunk: np.ndarray, callback=None):
        if chunk is None or len(chunk) == 0:
            return

        try:
            self.audio_queue.put_nowait(chunk)
        except queue.Full:
            # 队列满时丢弃最旧结果，优先保证实时性
            try:
                self.audio_queue.get_nowait()
                self.audio_queue.put_nowait(chunk)
            except queue.Empty:
                pass

        if callback:
            callback(chunk)

    def _capture_loop(self, callback: Optional[Callable[[np.ndarray], None]] = None):
        try:
            with self._loopback_mic.recorder(
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.internal_block_samples
            ) as recorder:
                print("音频捕获已启动，正在监听系统声音...")

                buffer_list = []
                total_samples = 0
                silent_count = 0

                while self.is_running:
                    data = recorder.record(numframes=self.internal_block_samples)
                    if data is None or len(data) == 0:
                        continue

                    # 转单声道
                    if data.ndim > 1:
                        data = data.mean(axis=1)

                    data = data.astype(np.float32)

                    buffer_list.append(data)
                    total_samples += len(data)

                    if self._is_silent(data):
                        silent_count += 1
                    else:
                        silent_count = 0

                    # 条件1：已达到最短长度，且尾部出现静音，认为一句话基本结束
                    if total_samples >= self.min_commit_samples and silent_count >= self.silence_blocks_to_commit:
                        chunk = np.concatenate(buffer_list, axis=0)
                        self._enqueue_chunk(chunk, callback)
                        buffer_list = []
                        total_samples = 0
                        silent_count = 0
                        continue

                    # 条件2：即使没有静音，也不能无限累积，超过上限强制提交
                    if total_samples >= self.max_commit_samples:
                        chunk = np.concatenate(buffer_list, axis=0)
                        self._enqueue_chunk(chunk, callback)
                        buffer_list = []
                        total_samples = 0
                        silent_count = 0

        except Exception as e:
            print(f"音频捕获错误: {e}")
            self.is_running = False

    def get_audio_chunk(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self):
        self.is_running = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)

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