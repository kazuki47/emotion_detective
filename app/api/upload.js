import { NextResponse } from 'next/server';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';

// バックエンドAPIのURL
const BACKEND_API_URL = 'http://localhost:8000/analyze'; // 実際のバックエンドURLに合わせて変更してください

export async function POST(request) {
  try {
    console.log('APIリクエスト受信: /api/upload');
    
    const formData = await request.formData();
    const file = formData.get('file');
    
    if (!file) {
      console.error('ファイルが見つかりません');
      return NextResponse.json(
        { error: 'ファイルが見つかりません' },
        { status: 400 }
      );
    }
    
    console.log(`ファイル情報: 名前=${file.name}, サイズ=${file.size}バイト, タイプ=${file.type}`);
    
    // ファイルサイズのチェック (フロントエンド側でも確認)
    if (file.size > 5 * 1024 * 1024) {
      console.error(`ファイルサイズ超過: ${file.size}バイト`);
      return NextResponse.json(
        { error: 'ファイルサイズが5MBを超えています' },
        { status: 400 }
      );
    }

    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
      // オリジナルのファイル名から拡張子を抽出
    const originalFilename = file.name;
    const fileExtension = path.extname(originalFilename);
    
    // 一意のファイル名を生成 (フロントエンドで表示用)
    const fileName = `${uuidv4()}${fileExtension}`;
      try {
      // ファイルをバックエンドAPIに送信
      const apiFormData = new FormData();
      
      // Next.js 13+では、File APIを使用してBlobからFileオブジェクトを作成する必要がある
      const fileBlob = new Blob([buffer], { type: file.type });
      const fileObject = new File([fileBlob], file.name, { type: file.type });
      apiFormData.append('file', fileObject);
      
      console.log(`バックエンドAPIにリクエスト送信: ${BACKEND_API_URL}`);
      
      // バックエンドAPIにリクエスト
      const backendResponse = await fetch(BACKEND_API_URL, {
        method: 'POST',
        body: apiFormData,
      });
      
      if (!backendResponse.ok) {
        let errorMessage = `バックエンドAPIエラー: ${backendResponse.status}`;
        try {
          const errorData = await backendResponse.json();
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          // JSONでない場合はテキストで取得
          const errorText = await backendResponse.text();
          console.error('バックエンドから非JSONレスポンス:', errorText);
          errorMessage = `バックエンドAPIエラー: ${errorText.substring(0, 100)}...`;
        }
        throw new Error(errorMessage);
      }
        // APIからの応答を解析
      let analysisResult;
      try {
        analysisResult = await backendResponse.json();
        console.log('バックエンドAPIからの応答:', analysisResult);
      } catch (jsonError) {
        console.error('JSONパースエラー:', jsonError);
        const responseText = await backendResponse.text();
        console.error('応答テキスト:', responseText.substring(0, 200));
        throw new Error('応答をJSONとして解析できませんでした');
      }
        
      // フロントエンドに処理結果を返す
      return NextResponse.json({ 
        success: true,
        fileName,
        originalName: originalFilename,
        // 感情分析の結果をフロントエンドが期待する形式に変換
        label: analysisResult.emotion // バックエンドは { emotion: "ラベル" } の形式で返す
      });} catch (error) {
      console.error('ファイル処理エラー:', error);
      return NextResponse.json(
        { error: error.message || 'ファイルの処理に失敗しました' },
        { status: 500 }
      );
    }
      } catch (error) {
    console.error('アップロードエラー:', error);
    return NextResponse.json(
      { error: error.message || 'ファイルのアップロードに失敗しました' },
      { status: 500 }
    );
  }
}