from snowflake import SnowflakeGenerator
from datetime import datetime
import zoneinfo

zone = zoneinfo.ZoneInfo("Asia/Tokyo")

class Snowflake:
    def generate() -> int:
        start_time = datetime(2024, 1, 1, 16, 10, 0, tzinfo=zone)
        gen = SnowflakeGenerator(instance=406, epoch=int(start_time.timestamp() * 1000.))
        return next(gen)