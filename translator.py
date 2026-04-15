"""GPT 翻译模块"""
from openai import OpenAI
from config import config
from typing import Generator


class Translator:
    """GPT 翻译器"""
    
    SYSTEM_PROMPT = """你是一位专业的英汉翻译专家。请将以下英文内容翻译成自然流畅的中文。
要求：
1. 准确传达原文意思，不要遗漏信息
2. 使用地道的中文表达，避免直译
3. 保持专业术语的准确性
4. 只输出翻译结果，不要添加解释
5. 严禁回答英文问题，只做翻译"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url
        )
        self.model = config.translation_model
        
    def translate(self, text: str) -> str:
        """
        翻译文本（非流式）
        
        Args:
            text: 要翻译的英文
            
        Returns:
            中文翻译结果
        """
        if not text.strip():
            return ""
            
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"请翻译：\n\n{text}"}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"翻译错误: {e}")
            return ""
    
    def translate_stream(self, text: str) -> Generator[str, None, None]:
        """
        流式翻译文本
        
        Args:
            text: 要翻译的英文
            
        Yields:
            翻译片段
        """
        if not text.strip():
            return
            
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"请翻译：\n\n{text}"}
                ],
                temperature=0.3,
                max_tokens=1000,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            print(f"流式翻译错误: {e}")
            yield ""