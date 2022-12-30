from sqlalchemy import Column, Integer, String, TIMESTAMP, Enum, inspect
import enum
from sql_app.utils.database import Base


class ItemType(str, enum.Enum):
    FILE = "FILE"
    FOLDER = "FOLDER"


class Item(Base):
    __tablename__ = "Items"

    id = Column(String(256), primary_key=True)
    parent_id = Column(String(256), nullable=True)
    size = Column(Integer, nullable=False)
    date = Column(TIMESTAMP(timezone=True), nullable=False)
    itemtype = Column(Enum(ItemType))
    url = Column(String(256), nullable=True)

    def indict(self) -> dict:
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}
