![アプリを起動した画像](image.jpg)

## □動作環境  
Python3.11以上

## □前準備

〇VOICEBOXのダウンロード  
公式サイトから取得  
URL：https://voicevox.hiroshiba.jp/

〇Gemini APIの取得  
Google AI Studioから取得  
URL：https://aistudio.google.com/  
・「Get API key」　→　「+ APIキーを作成」 →　「新しいプロジェクトでAPIキーを作成」  
・表示されたAPIキーをコピーし、安全な場所に保存

〇カレントディレクトリに「.env」追加  
・実行ファイルのあるフォルダで右クリック　→　新規作成　→　テキスト　→　名前：.env　※.txt拡張子も削除  
・「・env」をプロパティで開いて、「ファイルの種類：ENVファイル」を確認

〇「.env」に環境変数を追加  
・「.env」をメモ帳アプリなどで開く  
・2つの環境変数に値を入力する  
GOOGLE_API_KEY=取得したGemini APIキーを入力  
　例）GOOGLE_API_KEY=GeminiAPIKeyExample1234567890abcdef  
VOICEVOX_EXE_PATH=VOICEVOXの実行ファイルのパスを入力  
　例）VOICEVOX_EXE_PATH=C:\Users\ユーザー名\AppData\Local\Programs\VOICEVOX\voicevox.exe

〇必要なパッケージをターミナルでインストール  

```bash
pip install flet
pip install flet-audio
pip install python-dotenv
pip install google-generativeai
```

## □概要  
main.pyを起動すると、ダウンロードしたVOICEVOXとアプリが起動します。  
Geminiを使用する時と変わらずで、テキストベースでやり取りです。  
返答に選択したキャラクターの音声がつきます。

main.pyがあるカレントディレクトリに音声ファイルが自動作成されるのでアプリを終了する時などに、  
下側の「すべての .wav ファイルを削除」を押して、音声ファイルの削除推奨です。
