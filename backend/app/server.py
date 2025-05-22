# 完全に独立したサーバー起動スクリプト
from fastapi import FastAPI, APIRouter, UploadFile, File
import uvicorn
import sys
import os

# アプリケーションのパスを追加
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(app_dir)

# 必要なモジュールをインポート
from utils import validate_file, convert_to_wav
from model import model, feature_extractor
import torch
import soundfile as sf
import io

# FastAPIアプリケーションを作成
app = FastAPI()
router = APIRouter()

@router.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    contents = await validate_file(file)

    # .wav以外の形式ならffmpegで変換
    if not file.filename.endswith(".wav"):
        # ファイル名から拡張子を取得
        file_extension = os.path.splitext(file.filename)[1].lower()
        wav_bytes = convert_to_wav(contents, file_extension=file_extension)
    else:
        wav_bytes = contents

    audio_input, sample_rate = sf.read(io.BytesIO(wav_bytes))
    inputs = feature_extractor(audio_input, sampling_rate=sample_rate, return_tensors="pt", padding=True)

    with torch.no_grad():
        logits = model(**inputs).logits
        predicted_id = torch.argmax(logits, dim=-1).item()
        label = model.config.id2label[predicted_id]

    return {"emotion": label}

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
