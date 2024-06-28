import asyncpg
import asyncio
import yaml
import re
import os

if os.path.isfile(".env"):
    from dotenv import load_dotenv
    load_dotenv()

path_matcher = re.compile(r'\$\{([^}^{]+)\}')
def path_constructor(loader, node):
  ''' Extract the matched value, expand env variable, and replace the match '''
  value = node.value
  match = path_matcher.match(value)
  env_var = match.group()[2:-1]
  return os.environ.get(env_var) + value[match.end():]

yaml.add_implicit_resolver('!path', path_matcher)
yaml.add_constructor('!path', path_constructor)

with open("config.yml", "r", encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

database = config["database"]

async def main():
    """
    Migration the database.
    """
    conn: asyncpg.Connection = await asyncpg.connect(
        host=database["host"],
        port=database["port"],
        user=database["user"],
        password=database["pass"],
        database=database["name"]
    )
    prefix = database.get("prefix", "")
    try:
        await conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {prefix}users (
                id BIGINT NOT NULL PRIMARY KEY UNIQUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                domain VARCHAR(253),
                email VARCHAR(320) UNIQUE,
                password TEXT,
                handle VARCHAR(14) NOT NULL UNIQUE,
                display_name VARCHAR(16),
                icon_url TEXT,
                header_url TEXT,
                description VARCHAR(500),
                info JSON,
                public_key TEXT NOT NULL,
                private_key TEXT NOT NULL
            )
        ''')

        await conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {prefix}roles (
                id BIGINT NOT NULL PRIMARY KEY UNIQUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                users JSON,
                permissions JSON,
                color VARCHAR(6),
                icon_url TEXT,
                minimum_icon_url TEXT
            )
        ''')

        await conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {prefix}letters (
                id BIGINT NOT NULL PRIMARY KEY UNIQUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                user_id BIGINT NOT NULL,
                replyed_to BIGINT,
                relettered_to BIGINT,
                content VARCHAR(4000),
                attachments JSON
            )
        ''')

        await conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {prefix}emojis (
                id TEXT NOT NULL PRIMARY KEY UNIQUE,
                image_url TEXT NOT NULL
            )
        ''')

        await conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {prefix}reactions (
                id BIGINT NOT NULL PRIMARY KEY UNIQUE,
                letter_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                reaction TEXT NOT NULL
            )
        ''')

        await conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {prefix}tokens (
                token TEXT NOT NULL PRIMARY KEY UNIQUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                permission TEXT NOT NULL,
                user_id BIGINT NOT NULL
            )
        ''')

        await conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {prefix}emailcheck (
                token TEXT NOT NULL PRIMARY KEY UNIQUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                email TEXT NOT NULL,
                handle TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        print("ok.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # 接続を閉じる
        await conn.close()

asyncio.run(main())