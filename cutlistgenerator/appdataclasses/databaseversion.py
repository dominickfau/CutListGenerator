from . import dataclass, datetime



@dataclass
class DatabaseVersion:
    version: str
    date_updated: datetime.datetime
    id: int = None

    def __str__(self):
        return f"Version:{self.version}, Date Updated: {self.date_updated.date()}"
    
    def __eq__(self, o: object) -> bool:
        return self.version == o.version

    def __lt__(self, o: object) -> bool:
        return self.version < o.version

    def __le__(self, o: object) -> bool:
        return self.version <= o.version

    def __gt__(self, o: object) -> bool:
        return self.version > o.version

    def __ge__(self, o: object) -> bool:
        return self.version >= o.version
