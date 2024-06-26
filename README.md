# Nyantter
まだ開発中です
## How to run Nyantter
必要なもの

- Python 3.11.9 (3.12での動作確認はしていません)

venvなんて知らん  
まず、依存関係をインストールします。
```
pip install -r requirement.txt
or
python -m pip install -r requirement.txt
```
### Set up the config
config.ymlをいじってください
### Database migration
```
py migration.py
or
python3 migration.py
```
### Run the Nyantter
```
uvicorn main:app -host 0.0.0.0 -port 10000
```