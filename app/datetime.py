from datetime import datetime as dt

class datetime(dt):
    def __str__(self):
        return self.isoformat()