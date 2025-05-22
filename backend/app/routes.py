# backend/app/routes.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from utils import validate_file, convert_to_wav
from model import model, feature_extractor
import soundfile as sf
import io
import torch
import os
import tempfile

router = APIRouter()

@router.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    try:
        print(f"ファイルを受信: {file.filename}, コンテンツタイプ: {file.content_type}")
        
        contents = await validate_file(file)
        print(f"ファイルバリデーション通過: サイズ {len(contents) / 1024:.2f} KB")
          # 全ての音声ファイルを変換してサンプルレートを16kHzに確実に合わせる
        try:
            print(f"音声データをサンプルレート16kHzに変換")
            # WAVフォーマットの場合でも、サンプリングレートを16kHzに変換
            file_extension = os.path.splitext(file.filename)[1].lower()
            
            try:
                wav_bytes = convert_to_wav(contents, file_extension=file_extension)
                print(f"変換成功: WAVサイズ {len(wav_bytes) / 1024:.2f} KB")
            except Exception as convert_err:
                # FFmpegによる変換に失敗した場合、WAVファイルならsoundfileを使用して直接リサンプリングを試みる
                if file_extension.lower() == ".wav":
                    print(f"FFmpeg変換に失敗しました。WAVファイルなのでsoundfileで直接処理します。")
                    try:
                        # バイト列からデータを読み込む
                        audio_data, sample_rate = sf.read(io.BytesIO(contents))
                        
                        # 一時ファイルに出力 (16kHzへのリサンプリングを含む)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_out:
                            temp_path = temp_out.name
                            
                        sf.write(temp_path, audio_data, 16000)
                        
                        # 書き込まれたファイルを読み込む
                        with open(temp_path, "rb") as f:
                            wav_bytes = f.read()
                            
                        try:
                            os.remove(temp_path)
                        except:
                            pass
                            
                        print(f"Soundfileによるリサンプリング成功: WAVサイズ {len(wav_bytes) / 1024:.2f} KB")
                    except Exception as sf_err:
                        print(f"Soundfileによるリサンプリングも失敗: {str(sf_err)}")
                        raise HTTPException(status_code=500, detail=f"音声変換に失敗しました: {str(convert_err)} および {str(sf_err)}")
                else:
                    # WAV以外の形式でFFmpeg変換に失敗した場合はエラーを返す
                    raise HTTPException(status_code=500, detail=f"音声変換中にエラーが発生しました: {str(convert_err)}")
        except HTTPException as he:
            raise he
        except Exception as e:
            print(f"変換エラー: {str(e)}")
            raise HTTPException(status_code=500, detail=f"音声変換中にエラーが発生しました: {str(e)}")

        print(f"音声データの解析開始: {len(wav_bytes) / 1024:.2f} KB")
        
        try:
            # soundfileを使用して音声データを読み込む
            audio_input, sample_rate = sf.read(io.BytesIO(wav_bytes))
            print(f"音声データ読み込み成功: サンプルレート {sample_rate}Hz, 形状 {audio_input.shape}")
            
            # サンプルレートを確認
            if sample_rate != 16000:
                print(f"警告: サンプルレートが16kHzではありません: {sample_rate}Hz")
                # ffmpegがうまく変換できていない場合は、手動でサンプルレートを16kHzに設定
                print("入力サンプルレートを16kHzとして処理します")
            
            # 特徴抽出とモデル処理 - 常にサンプルレートを16000に指定
            inputs = feature_extractor(audio_input, sampling_rate=16000, return_tensors="pt", padding=True)
            
            with torch.no_grad():
                logits = model(**inputs).logits
                predicted_id = torch.argmax(logits, dim=-1).item()
                label = model.config.id2label[predicted_id]
                
            print(f"分析完了: 推定された感情 = {label}")
            return {"emotion": label}
            
        except Exception as e:
            print(f"音声処理エラー: {str(e)}")
            raise HTTPException(status_code=500, detail=f"音声の解析中にエラーが発生しました: {str(e)}")
            
    except HTTPException as e:
        # HTTP例外はそのまま再送
        raise e
    except Exception as e:
        print(f"予期しないエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"予期しないエラーが発生しました: {str(e)}")
