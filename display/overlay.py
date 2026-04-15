"""悬浮字幕窗口模块"""
import tkinter as tk
from tkinter import font as tkfont
import threading
from config import config


class OverlayWindow:
    """悬浮字幕窗口"""
    
    def __init__(self):
        self.root: tk.Tk | None = None
        self.original_label: tk.Label | None = None
        self.translation_label: tk.Label | None = None
        self.is_running = False
        self.window_thread: threading.Thread | None = None
        self.opacity = config.overlay_opacity
        
    def _create_window(self):
        """创建窗口（在独立线程中运行）"""
        self.root = tk.Tk()
        self.root.title("实时翻译")
        
        # 窗口属性
        self.root.overrideredirect(True)  # 无边框
        self.root.attributes('-topmost', True)  # 置顶
        self.root.attributes('-alpha', self.opacity)  # 透明度
        self.root.configure(bg='black')
        
        # 位置和大小
        screen_width = self.root.winfo_screenwidth()
        window_width = 800
        window_height = 120
        x = (screen_width - window_width) // 2
        y = 50  # 顶部距离
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 字体
        original_font = tkfont.Font(family="Segoe UI", size=14, weight="normal")
        translation_font = tkfont.Font(family="Microsoft YaHei", size=16, weight="bold")
        
        # 原文标签
        self.original_label = tk.Label(
            self.root,
            text="等待音频...",
            font=original_font,
            fg="#4A90D9",  # 蓝色
            bg="black",
            wraplength=780,
            justify="center"
        )
        self.original_label.pack(pady=(10, 5))
        
        # 译文标签
        self.translation_label = tk.Label(
            self.root,
            text="",
            font=translation_font,
            fg="#FFFFFF",  # 白色
            bg="black",
            wraplength=780,
            justify="center"
        )
        self.translation_label.pack(pady=(5, 10))
        
        # 拖动功能
        self._setup_drag()
        
        # 右键菜单
        self._setup_context_menu()
        
        self.is_running = True
        self.root.mainloop()
        self.is_running = False
        
    def _setup_drag(self):
        """设置窗口拖动"""
        def start_drag(event):
            self.root._drag_start_x = event.x
            self.root._drag_start_y = event.y
            
        def do_drag(event):
            x = self.root.winfo_x() + event.x - self.root._drag_start_x
            y = self.root.winfo_y() + event.y - self.root._drag_start_y
            self.root.geometry(f"+{x}+{y}")
            
        self.root.bind("<Button-1>", start_drag)
        self.root.bind("<B1-Motion>", do_drag)
        
    def _setup_context_menu(self):
        """设置右键菜单"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="关闭", command=self.stop)
        
        def show_menu(event):
            menu.post(event.x_root, event.y_root)
            
        self.root.bind("<Button-3>", show_menu)
        
    def start(self):
        """启动悬浮窗口"""
        if not config.show_overlay:
            return
            
        self.window_thread = threading.Thread(target=self._create_window)
        self.window_thread.daemon = True
        self.window_thread.start()
        
    def update_text(self, original: str, translation: str):
        """更新显示文本"""
        if self.root and self.is_running:
            def _update():
                if self.original_label:
                    self.original_label.config(text=original[:200])  # 限制长度
                if self.translation_label:
                    self.translation_label.config(text=translation[:200])
            self.root.after(0, _update)
            
    def clear(self):
        """清空显示"""
        self.update_text("", "")
        
    def stop(self):
        """关闭窗口"""
        if self.root:
            def _stop():
                self.root.quit()
                self.root.destroy()
            try:
                self.root.after(0, _stop)
            except:
                pass
        self.is_running = False