import asyncpg
import asyncio
import yaml

with open("config.yml") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

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
                created_at TIMESTAMP DEFAULT now(),
                email VARCHAR(320) NOT NULL UNIQUE,
                password TEXT NOT NULL,
                handle VARCHAR(14) NOT NULL UNIQUE,
                display_name VARCHAR(16),
                description VARCHAR(500),
                info JSON
            )
        ''')

        await conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {prefix}letters (
                id BIGINT NOT NULL PRIMARY KEY UNIQUE,
                created_at TIMESTAMP DEFAULT now(),
                user_id BIGINT NOT NULL,
                replyed_to BIGINT,
                relettered_to BIGINT,
                content VARCHAR(4000)
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
                created_at TIMESTAMP DEFAULT now(),
                permission TEXT NOT NULL,
                user_id BIGINT NOT NULL
            )
        ''')

        print("ok.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # 接続を閉じる
        await conn.close()

asyncio.run(main())