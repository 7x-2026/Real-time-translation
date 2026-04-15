"""主程序入口"""
import sys
import signal
import time
import threading
from pathlib import Path

# 添加项目目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from audio_capture import AudioCapture
from transcriber import Transcriber
from translator import Translator
from display import ConsoleDisplay, OverlayWindow, TranslationLogger



class RealtimeTranslator:
    """实时翻译器主类"""
    
    def __init__(self):
        self.config = config
        self.audio_capture: AudioCapture | None = None
        self.transcriber: Transcriber | None = None
        self.translator: Translator | None = None
        self.console: ConsoleDisplay | None = None
        self.overlay: OverlayWindow | None = None
        self.logger: TranslationLogger | None = None
        self.is_running = False
        
    def initialize(self) -> bool:
        """初始化组件"""
        # 验证配置
        if not self.config.validate():
            return False
            
        try:
            # 初始化显示模块
            self.console = ConsoleDisplay()
            self.console.print_header()
            self.console.print_info("正在初始化组件...")
            
            # 初始化音频捕获
            self.console.update_status("初始化音频设备...")
            self.audio_capture = AudioCapture()
            
            # 初始化 OpenAI 组件
            self.console.update_status("连接 OpenAI API...")
            self.transcriber = Transcriber()
            self.translator = Translator()
            
            # 初始化日志
            self.logger = TranslationLogger()
            
            # 初始化悬浮窗口
            if self.config.show_overlay:
                self.overlay = OverlayWindow()
                self.overlay.start()
                time.sleep(0.5)  # 等待窗口创建
            
            self.console.print_success("初始化完成！")
            self.console.print_info("开始监听系统音频...")
            self.console.console.print()
            
            return True
            
        except Exception as e:
            if self.console:
                self.console.print_error(f"初始化失败: {e}")
            else:
                print(f"初始化失败: {e}")
            return False
            
    def process_audio_chunk(self, audio_data):
        """处理音频片段"""
        try:
            # 语音识别
            self.console.update_status("识别中...")
            original_text = self.transcriber.transcribe(audio_data)
            
            if not original_text.strip():
                return
                
            # 翻译
            self.console.update_status("翻译中...")
            translation = self.translator.translate(original_text)
            
            if not translation.strip():
                return
                
            # 输出结果
            self.console.print_translation(original_text, translation)
            
            # 更新悬浮窗口
            if self.overlay:
                self.overlay.update_text(original_text, translation)
                
            # 记录到文件
            if self.logger:
                self.logger.log(original_text, translation)
                
        except Exception as e:
            self.console.print_error(f"处理错误: {e}")
            
    def run(self):
        """运行主循环"""
        if not self.initialize():
            return
            
        self.is_running = True
        
        # 设置信号处理
        def signal_handler(sig, frame):
            print("\n正在停止...")
            self.stop()
            
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            # 启动音频捕获
            self.audio_capture.start()
            
            # 主处理循环
            while self.is_running:
                audio_data = self.audio_capture.get_audio_chunk(timeout=1.0)
                if audio_data is not None:
                    self.process_audio_chunk(audio_data)
                    
        except KeyboardInterrupt:
            print("\n收到中断信号")
        finally:
            self.stop()
            
    def stop(self):
        """停止程序"""
        self.is_running = False
        
        if self.audio_capture:
            self.audio_capture.stop()
            
        if self.overlay:
            self.overlay.stop()
            
        if self.console:
            self.console.print_success("程序已退出")


def main():
    """程序入口"""
    translator = RealtimeTranslator()
    translator.run()


if __name__ == "__main__":
    main()