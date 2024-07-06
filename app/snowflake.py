from snowflake import SnowflakeGenerator
from datetime import datetime

class Snowflake:
    gen = SnowflakeGenerator(
        instance=406,
        epoch=0,
        timestamp=int(datetime.now().timestamp() * 1000),
    )
    
    def generate() -> int:
        return next(gen)
