from modelscope.hub.snapshot_download import snapshot_download

# 你用的模型名称
model_name = "FunAudioLLM/SenseVoiceSmall"

# 下载/获取模型路径
model_path = snapshot_download(model_name)

print("✅ 你的模型绝对路径：")
print(model_path)