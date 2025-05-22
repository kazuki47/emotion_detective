'use client';
import * as React from 'react';
import { Header } from '../components/Header';
import { Button } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const DetectionPage = () => {
  const [selectedFile, setSelectedFile] = React.useState(null);
  const [fileName, setFileName] = React.useState('');
  const [uploading, setUploading] = React.useState(false);
  const [uploadStatus, setUploadStatus] = React.useState(null);
  const [emotionLabel, setEmotionLabel] = React.useState(null); // 感情ラベルのための状態
  const fileInputRef = React.useRef(null);

  const handleFileUpload = () => {
    fileInputRef.current.click();
  };
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setFileName(file.name);
      setUploadStatus(null);
      
      // ファイルサイズチェック (5MB制限)
      if (file.size > 5 * 1024 * 1024) {
        setUploadStatus({
          success: false,
          message: 'エラー: ファイルサイズが5MBを超えています'
        });
        return;
      }
      
      // 音声・動画ファイルの長さをチェック
      checkAudioDuration(file).then(isValid => {
        if (isValid) {
          uploadFile(file);
        }
      });
    }
  };

  // 音声・動画ファイルの長さをチェックする関数
  const checkAudioDuration = (file) => {
    return new Promise(resolve => {
      // ブラウザのMedia APIを使用して長さを取得
      const audio = document.createElement(file.type.startsWith('video') ? 'video' : 'audio');
      audio.preload = 'metadata';
      
      audio.onloadedmetadata = () => {
        window.URL.revokeObjectURL(audio.src);
        
        if (audio.duration > 20) {
          setUploadStatus({
            success: false,
            message: 'エラー: ファイルの長さが20秒を超えています'
          });
          resolve(false);
        } else {
          resolve(true);
        }
      };
      
      audio.onerror = () => {
        window.URL.revokeObjectURL(audio.src);
        console.warn('ファイルの長さを確認できませんでした。アップロードを続行します。');
        resolve(true); // バックエンド側でも検証されるので続行
      };
      
      audio.src = URL.createObjectURL(file);
    });
  };  const uploadFile = async (file) => {
    if (!file) return;
    
    try {
      setUploading(true);
      setEmotionLabel(null); // アップロード開始時にラベルをリセット
      
      const formData = new FormData();
      formData.append('file', file);
      
      console.log(`ファイルをアップロード: ${file.name}, サイズ: ${(file.size / 1024 / 1024).toFixed(2)}MB, タイプ: ${file.type}`);
      
      // 改善: タイムアウト付きのfetch
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30秒タイムアウト
      
      try {
        const response = await fetch('/api/upload', {
          method: 'POST',
          body: formData,
          signal: controller.signal
        });
      
        clearTimeout(timeoutId); // タイムアウトをクリア
        
        // ステータスコードを確認してログ出力
        console.log(`APIレスポンスステータス: ${response.status}`);
        
        // レスポンスをクローンしてテキストとJSONの両方で読み取れるようにする
        const responseClone = response.clone();
        
        let data;
        try {
          data = await response.json();
          console.log('APIレスポンスデータ:', data);
        } catch (parseError) {
          console.error('JSONパースエラー:', parseError);
          // レスポンスのクローンからテキストを取得
          const rawText = await responseClone.text();
          console.error('受信した生のレスポンス:', rawText.substring(0, 500));
          throw new Error(`APIからの応答をJSONとして解析できませんでした: ${parseError.message}`);
        }
        
        if (response.ok) {
          console.log('アップロード成功:', data);
          setUploadStatus({
            success: true,
            message: 'ファイルが正常にアップロードされました'
          });
          
          // APIレスポンスから感情ラベルを取得して保存
          if (data.label) {
            setEmotionLabel(data.label);
            console.log('感情ラベル検出:', data.label);
          } else {
            console.warn('レスポンスにラベルがありません:', data);
          }
        } else {
          console.error('APIエラーレスポンス:', data);
          setUploadStatus({
            success: false,
            message: `エラー: ${data.error || 'アップロードに失敗しました'}`
          });
        }
      } catch (fetchError) {
        clearTimeout(timeoutId);
        if (fetchError.name === 'AbortError') {
          console.error('リクエストがタイムアウトしました');
          throw new Error('リクエストがタイムアウトしました。サーバーが応答していません。');
        }
        throw fetchError;
      }    } catch (error) {
      console.error('アップロードエラー:', error);
      setUploadStatus({
        success: false,
        message: `アップロード中に問題が発生しました: ${error.message}`
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
        <Header />
        <main>
            <h1 className="text-2xl font-bold text-center mt-8">感情認識アプリ</h1>            <div className="flex justify-center mt-8">                <div className="border-2 border-dashed border-gray-400 p-8 rounded-lg" style={{ maxWidth: '500px', width: '100%' }}>
                    <input 
                        type="file" 
                        accept="audio/*,video/*" 
                        className="hidden" 
                        ref={fileInputRef} 
                        onChange={handleFileChange}
                    />                          
                    <Button 
                        variant="contained" 
                        color="primary"
                        onClick={handleFileUpload}
                        disabled={uploading}
                        sx={{ 
                            width: '300px', 
                            display: 'flex', 
                            margin: '0 auto', 
                            justifyContent: 'center', 
                            alignItems: 'center'
                        }}
                    >
                        <CloudUploadIcon sx={{ mr: 1 }} />
                        {uploading ? '処理中...' : '音声・動画をアップロード'}
                    </Button>
                    
                    <div className="mt-4 text-sm text-gray-600 text-center">
                      <p>制限: 最大5MB、最長20秒まで</p>
                      <p>対応形式: mp3, mp4, wav, mov, avi など</p>
                    </div>
                    
                    {fileName && (
                        <p className="mt-2 text-gray-600">選択されたファイル: {fileName}</p>
                    )}
                    {uploadStatus && (
                        <div className={`mt-4 p-2 rounded ${uploadStatus.success ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                            {uploadStatus.message}
                        </div>
                    )}
                    
                    {/* 感情認識の結果表示エリア */}
                    {emotionLabel && (
                        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                            <h3 className="text-lg font-semibold text-center mb-2">感情認識結果</h3>
                            <div className="text-center text-xl font-bold text-blue-700">
                                {emotionLabel}
                            </div>
                        </div>
                    )}
                    
                    <p className="text-sm text-gray-500 mt-4">
                        ※音声ファイル(.mp3, .wav など)、動画ファイル(.mp4, .mov など) <br />
                        ※ファイルサイズは最大5MB、長さ20秒まで <br />
                    </p>
                </div>
            </div>
        </main>
    </div>
  );
}

export default DetectionPage;