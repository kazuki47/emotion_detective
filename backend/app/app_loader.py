# バックエンドサーバーを起動するためのスクリプト（シンプル版）
import os
import sys

# カレントディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# FastAPIアプリをインポート
from main import app

# ここではアプリを実行せず、uvicornコマンドラインから実行します
