# バックエンドサーバーを起動するためのスクリプト
import uvicorn
import os
import sys

# カレントディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

if __name__ == "__main__":
    # main.pyのappオブジェクトを起動
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
