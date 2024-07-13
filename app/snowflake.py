from datetime import datetime

from snowflake import SnowflakeGenerator


class Snowflake:
    gen = SnowflakeGenerator(
        instance=406,
        epoch=0,
        timestamp=int(datetime.now().timestamp() * 1000),
    )

    @classmethod
    def generate(cls) -> int:
        return next(cls.gen)