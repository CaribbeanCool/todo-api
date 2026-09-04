from sqlalchemy import Boolean, Column, Integer, String

from todo_api.database import Base


class TodoDB(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    done = Column(Boolean, default=False)
