"""文件日志模块"""
from datetime import datetime
from pathlib import Path
from config import config


class TranslationLogger:
    """翻译记录器"""
    
    def __init__(self, log_file: str = "translation_log.txt"):
        self.log_path = Path(log_file)
        self._init_file()
        
    def _init_file(self):
        """初始化日志文件"""
        if not self.log_path.exists():
            with open(self.log_path, 'w', encoding='utf-8') as f:
                f.write(f"# 实时翻译记录\n")
                f.write(f"# 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# " + "="*50 + "\n\n")
                
    def log(self, original: str, translation: str):
        """记录翻译"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}]\n")
            f.write(f"原文: {original}\n")
            f.write(f"译文: {translation}\n")
            f.write("-" * 50 + "\n")
            
    def get_recent(self, count: int = 10) -> list[dict]:
        """获取最近的记录"""
        if not self.log_path.exists():
            return []
            
        records = []
        with open(self.log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # 解析最后 count 条记录
        current_record = {}
        for line in reversed(lines):
            line = line.strip()
            if line.startswith('[') and ']' in line:
                if current_record:
                    records.append(current_record)
                    if len(records) >= count:
                        break
                current_record = {'time': line[1:-1]}
            elif line.startswith('原文: '):
                current_record['original'] = line[4:]
            elif line.startswith('译文: '):
                current_record['translation'] = line[4:]
                
        return list(reversed(records))