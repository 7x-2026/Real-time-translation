"""控制台美化输出模块"""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from datetime import datetime


class ConsoleDisplay:
    """Rich 控制台显示器"""
    
    def __init__(self):
        self.console = Console()
        self.current_text = ""
        self.translation_text = ""
        self.status = "等待中"
        
    def print_header(self):
        """打印标题"""
        self.console.print(Panel.fit(
            "[bold blue]🎙️ 实时英语翻译器[/bold blue]\n"
            "[dim]按 Ctrl+C 停止程序[/dim]",
            border_style="blue"
        ))
        self.console.print()
        
    def print_translation(self, original: str, translation: str):
        """打印翻译结果"""
        time_str = datetime.now().strftime("%H:%M:%S")
        
        # 原文（绿色）
        self.console.print(f"[dim]{time_str}[/dim] [green]📝 原文:[/green]")
        self.console.print(f"[white]{original}[/white]")
        
        # 译文（黄色）
        self.console.print(f"[yellow]🔄 译文:[/yellow]")
        self.console.print(f"[bold yellow]{translation}[/bold yellow]")
        self.console.print("─" * 50)
        
    def update_status(self, status: str):
        """更新状态"""
        self.status = status
        status_colors = {
            "录音中": "green",
            "识别中": "blue",
            "翻译中": "yellow",
            "等待中": "dim"
        }
        color = status_colors.get(status, "white")
        self.console.print(f"[{color}]● {status}[/{color}]", end="\r")
        
    def print_info(self, message: str):
        """打印信息"""
        self.console.print(f"[dim]{message}[/dim]")
        
    def print_error(self, message: str):
        """打印错误"""
        self.console.print(f"[bold red]❌ {message}[/bold red]")
        
    def print_success(self, message: str):
        """打印成功"""
        self.console.print(f"[bold green]✓ {message}[/bold green]")