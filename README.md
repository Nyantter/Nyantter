# Nyantter
まだ開発中です
## Todo
- [ ] フロントエンド (5/9)
    - [x] 登録
    - [x] メール認証
    - [x] ログイン
    - [ ] タイムライン (2/4)
        - [x] レターを投稿したユーザーの表示
        - [x] レターの内容の表示
        - [ ] リアクションの表示
        - [ ] リアクションをつける・リプライ・リレター
    - [ ] プロフィール
    - [ ] 設定
- [ ] バックエンド (11/20)
    - [x] 認証 (5/5)
        - [x] アカウント登録
        - [x] メール送信
        - [x] メール認証
        - [x] トークン発行
        - [x] ログイン
    - [ ] ユーザー (0/3)
        - [ ] ユーザープロフィールの変更
        - [ ] パスワードの変更
        - [ ] アカウントの削除
    - [ ] 投稿 (6/7)
        - [x] ローカルタイムライン
        - [x] 投稿を作成
        - [x] 投稿を編集
        - [x] 投稿を削除
        - [x] リプライ・リレター
        - [x] リアクションをつける
        - [ ] ファイルのアップロード(imgur.com 経由？)
    - [ ] ActivityPub (1/5)
        - [x] NodeInfo
        - [ ] レターの配送
        - [ ] リアクションの配送
        - [ ] ユーザーの転送
        - [ ] アカウントの引っ越し
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