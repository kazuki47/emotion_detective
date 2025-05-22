# backend/app/utils.py

from fastapi import UploadFile, HTTPException
import ffmpeg
import tempfile
import subprocess
import os

MAX_SIZE_MB = 5
MAX_DURATION_SEC = 20

async def validate_file(file: UploadFile):
    import os
    
    contents = await file.read()
    # ファイルサイズのチェック
    if len(contents) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"ファイルサイズが{MAX_SIZE_MB}MBを超えています")
    
    print(f"ファイルを受信: {file.filename}, サイズ: {len(contents) / 1024 / 1024:.2f} MB")
    
    # 音声・動画ファイルの場合、長さをチェック
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension in ['mp3', 'mp4', 'wav', 'mov', 'avi', 'ogg', 'm4a']:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name
        
        try:
            duration = get_audio_duration(temp_path)
            print(f"ファイル長さ: {duration}秒")
            if duration > MAX_DURATION_SEC:
                # 一時ファイルを削除
                try:
                    os.remove(temp_path)
                except:
                    pass
                raise HTTPException(status_code=400, detail=f"ファイルの長さが{MAX_DURATION_SEC}秒を超えています")
            
            # 一時ファイルを削除
            try:
                os.remove(temp_path)
            except:
                pass
        except Exception as e:
            # 一時ファイルを削除
            try:
                os.remove(temp_path)
            except:
                pass
            # 長さの確認ができない場合でもファイル自体は受け付ける
            print(f"ファイルの長さを確認できませんでした: {str(e)}")
            
    return contents

def get_audio_duration(file_path):
    """
    ffprobeを使用して音声・動画ファイルの長さを秒単位で取得する
    
    Args:
        file_path: ファイルパス
    
    Returns:
        長さ（秒）
    """
    try:
        probe = ffmpeg.probe(file_path)
        # durationを検索
        if 'format' in probe and 'duration' in probe['format']:
            return float(probe['format']['duration'])
        # ストリーム情報から探す
        for stream in probe['streams']:
            if 'duration' in stream:
                return float(stream['duration'])
        # 見つからない場合はエラー
        raise ValueError("ファイルから長さを取得できませんでした")
    except Exception as e:
        raise Exception(f"ファイルの長さを確認できませんでした: {str(e)}")

def convert_to_wav(input_bytes: bytes, file_extension: str = ".mp4") -> bytes:
    """
    音声ファイルをWAVフォーマット（16kHz、モノラル）に変換する。
    FFmpeg-pythonのAPIを使用し、サブプロセスのフォールバックも実装。
    """
    input_path = None
    output_path = None
    
    try:
        # 入力ファイルを一時ファイルとして保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as input_temp:
            input_temp.write(input_bytes)
            input_path = input_temp.name

        # 出力ファイルのパスを生成
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as output_temp:
            output_path = output_temp.name
    
        print(f"変換開始: {input_path} -> {output_path}")
        
        # 実際のファイルパスを確認
        if not os.path.exists(input_path):
            print(f"警告: 入力ファイルが見つかりません: {input_path}")
            raise Exception(f"入力ファイルが見つかりません: {input_path}")
            
        # まず、ffmpeg-pythonを使用して変換を試みる
        try:
            (
                ffmpeg
                .input(input_path)
                .output(output_path, format='wav', ac=1, ar='16000')
                .run(quiet=True, overwrite_output=True)
            )
            print("FFmpeg-pythonでの変換成功")
        except Exception as ffmpeg_error:
            print(f"FFmpeg-pythonでの変換失敗: {str(ffmpeg_error)}、サブプロセスでの実行を試みます")
            
            # ffmpeg-python APIが失敗した場合、直接サブプロセスとしてffmpegを呼び出す
            try:
                import shutil
                ffmpeg_path = shutil.which('ffmpeg')
                
                if not ffmpeg_path:
                    # ダウンロード済みのffmpegがある場合は、そのパスを指定
                    possible_ffmpeg_paths = [
                        # Windowsでよくあるインストール場所
                        r"C:\ffmpeg\bin\ffmpeg.exe",
                        # アプリケーションのディレクトリにffmpegがある場合
                        os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe")
                    ]
                    
                    for path in possible_ffmpeg_paths:
                        if os.path.exists(path):
                            ffmpeg_path = path
                            break
                            
                    if not ffmpeg_path:
                        raise Exception("FFmpegが見つかりません。システムにインストールしてPATHに追加するか、アプリケーションディレクトリに配置してください。")
                
                # ffmpegコマンドを実行
                command = [
                    ffmpeg_path,
                    '-i', input_path,
                    '-ac', '1',
                    '-ar', '16000',
                    '-f', 'wav',
                    '-y',
                    output_path
                ]
                
                print(f"FFmpegコマンドを実行: {' '.join(command)}")
                
                process = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if process.returncode != 0:
                    raise Exception(f"FFmpegコマンド実行エラー: {process.stderr}")
                
                print("FFmpegコマンド実行成功")
                
            except Exception as subprocess_error:
                # 元のバイトをそのままWAV形式で返すフォールバック
                print(f"FFmpegサブプロセス実行エラー: {str(subprocess_error)}")
                raise Exception(f"FFmpegでの変換に失敗しました: {str(subprocess_error)}")
        
        # 変換されたWAVファイルが存在することを確認
        if not os.path.exists(output_path):
            raise Exception(f"変換後のWAVファイルが見つかりません: {output_path}")
            
        # 変換されたWAVファイルを読み込む
        with open(output_path, "rb") as f:
            wav_data = f.read()
            
        if len(wav_data) == 0:
            raise Exception("変換後のWAVファイルが空です")
        
        print(f"WAVファイル読み込み成功: {len(wav_data) / 1024:.2f} KB")
        return wav_data
        
    except Exception as e:
        print(f"音声変換エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"音声ファイルの変換に失敗しました: {str(e)}")
        
    finally:
        # 常に一時ファイルを削除する
        try:
            if input_path and os.path.exists(input_path):
                os.remove(input_path)
                print(f"入力一時ファイル削除: {input_path}")
            if output_path and os.path.exists(output_path):
                os.remove(output_path)
                print(f"出力一時ファイル削除: {output_path}")
        except Exception as cleanup_error:
            print(f"一時ファイル削除エラー: {cleanup_error}")
            # 削除に失敗してもエラーにしない
            pass
