# Nyantter
まだ開発中です
## Todo
- [ ] フロントエンド
    - [x] 登録
    - [x] ログイン
    - [x] タイムライン
    - [ ] 設定など
- [x] メール送信
- [x] アカウント登録
- [x] トークン発行
- [x] ログイン
- [x] ローカルタイムライン
- [ ] 投稿を作成・リプライ・リレター
- [ ] ユーザープロフィールの変更
- [ ] ファイルのアップロード
- [ ] リアクションをつける
- [ ] ActivityPub
## How to run Nyantter
必要なもの

- Python 3.11.9 (3.12での動作確認はしていません)
- (将来的に)Turnstileのサイトキー・シークレットキー

<small>venvなんて知らん</small>  
まず、依存関係をインストールします。
```
pip install -r requirements.txt
or
python -m pip install -r requirements.txt
```
### Set up the config
`config-example.yml`を`config.yml`へコピーし、`config.yml`を編集してください。
### Database migration
config.ymlの`database`の値が設定されているか確認してから、以下のコマンドを実行してください。
```
py migration.py
or
python3 migration.py
```
### Run the Nyantter
以下のコマンドでは、IPアドレス`0.0.0.0`、ポート`10000`でリッスンします。
```
uvicorn main:app -host 0.0.0.0 -port 10000
```