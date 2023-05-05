import uuid

import config
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy_utils import EmailType, UUIDType

Base = declarative_base()
engine = create_async_engine(config.PG_DSN)

Session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False  # type: ignore
)


class User(Base):
    __tablename__ = "ads_users"

    id = Column(Integer, primary_key=True)
    email = Column(EmailType, unique=True, index=True)
    password = Column(String(60), nullable=False)
    registration_time = Column(DateTime, server_default=func.now())


class Token(Base):
    __tablename__ = "tokens"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    creation_time = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey("ads_users.id", ondelete="CASCADE"))
    user = relationship("User", lazy="joined")


class Advert(Base):
    __tablename__ = "adverts"

    id = Column(Integer, primary_key=True)
    title = Column(String(40), unique=True, index=True)
    description = Column(String(120))
    creation_time = Column(DateTime, server_default=func.now())
    owner_id = Column(Integer, ForeignKey("ads_users.id", ondelete="CASCADE"))
    owner = relationship("User", lazy="joined")

    def __repr__(self) -> str:
        return (f"title: {self.title}, "
                f"description: {self.description}, "
                f"creation_time: {self.creation_time}, "
                f"owner_id: {self.owner_id}, ")


ORM_TYPE = User | Advert | Token
