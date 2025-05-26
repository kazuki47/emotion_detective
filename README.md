このプロジェクトは、[`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app)を使用して作成された[Next.js](https://nextjs.org)プロジェクトです。

## はじめに

まず、開発サーバーを起動します：

```bash
npm run dev
# または
yarn dev
# または
pnpm dev
# または
bun dev
```

ブラウザで[http://localhost:3000](http://localhost:3000)を開いて、結果を確認してください。

このプロジェクトでは、[`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts)を使用して、フォントの最適化と自動読み込みを行っています。

## バックエンドの実行方法

バックエンドサーバーを実行するには、以下の手順に従ってください：

1. バックエンドディレクトリに移動します：

   ```bash
   cd backend/app
   ```

2. 仮想環境を作成して有効化します（推奨）：

   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windowsの場合
   ```

3. 必要な依存関係をインストールします：

   ```bash
   pip install -r requirements.txt
   ```

4. バックエンドサーバーを起動します：

   ```bash
   python run_server.py
   ```

   または、`uvicorn`を使用してサーバーを起動することもできます：

   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```

5. バックエンドAPIにアクセスします：[http://127.0.0.1:8000](http://127.0.0.1:8000)
