from __future__ import annotations
from sqlalchemy import Column, Integer, String, DateTime
from fishbowlorm import Base
from fishbowlorm.models.basetables import ORM


class FBDatabaseVersion(Base):
    __tablename__ = 'databaseversion'

    id = Column(Integer, primary_key=True)
    alterCommand = Column(String(255))
    dateUpdated = Column(DateTime)
    version = Column(String(255))

    @staticmethod
    def find_current_version(orm: ORM) -> FBDatabaseVersion:
        return orm.session.query(FBDatabaseVersion).order_by(FBDatabaseVersion.id.desc()).first()


    @staticmethod
    def split_version(version: str) -> tuple[int, int]:
        """Splits the version string into release_year and version_number."""
        release_year, version_number = version.split('.')
        return int(release_year), int(version_number)


    @property
    def version_number(self) -> int:
        """Returns the version number of the database."""
        return self.split_version(self.version_string)[1]
    
    @property
    def version_string(self) -> str:
        """Returns the version string of the database."""
        return self.alterCommand.split("Fishbowl v")[1]