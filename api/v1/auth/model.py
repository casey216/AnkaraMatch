from sqlalchemy import Integer, Column, String
from api.v1.core.database import Base


class User(Base):
    __tablename__ = "auth"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)