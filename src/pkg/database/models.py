from typing import Any, List
from sqlalchemy_utils import create_database, database_exists
from sqlalchemy import (create_engine, Column, Integer, String, DateTime, func, ForeignKey, Boolean, Float,
                        UUID, CheckConstraint)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import base
from config.main import Config
import uuid

cfg = Config("config/config.yml").load()

url = (f"postgresql://{cfg['database']['user']}:{cfg['database']['password']}@{cfg['database']['host']}:"
       f"{cfg['database']['port']}/{cfg['database']['name']}")

if not database_exists(url):
    create_database(url)
engine = create_engine(url,
                       pool_pre_ping=True,
                       connect_args={
                           "keepalives_idle": 30,
                           "keepalives_interval": 10,
                           "keepalives_count": 5
                       },
                       pool_size=100,
                       max_overflow=50)

connection = engine.connect()
Session = sessionmaker(bind=engine)
session = Session()


class Base(declarative_base()):
    __abstract__ = True

    def __repr__(self):
        try:
            return "<{0.__class__.__name__}(id={0.id!r})>".format(self)
        except AttributeError:
            return "<{0.__class__.__name__}>".format(self)

    def save(self):
        with Session() as session:
            try:
                session.add(self)
            except InvalidRequestError:
                pass
            try:
                session.commit()
            except AttributeError:
                session.commit()
            session.refresh(self)
            return self

    def delete(self):
        with Session() as session:
            session.delete(self)
            session.commit()

    @classmethod
    def get(cls: base, **kwargs):
        """
        return one or none object
        :param kwargs:
        :return:
        """
        with Session() as session:
            obj: cls = session.query(cls).filter_by(**kwargs).one_or_none()
        return obj

    @classmethod
    def get_all(cls: base, **kwargs):
        order = kwargs.pop('order', None)
        limit = kwargs.pop('limit', None)
        offset = kwargs.pop('offset', None)
        with Session() as session:
            objects: List[cls] = session.query(cls).filter_by(**kwargs).order_by(order).limit(limit).offset(
                offset).all()
        return objects

    @classmethod
    def update_field(cls, field: str, new_value: Any, **kwargs):
        with Session() as session:
            session.query(cls).filter_by(**kwargs).update({field: new_value})
            session.commit()


class Client(Base):
    __tablename__ = 'client'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(UUID, default=uuid.uuid4, index=True)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)
    registration_date = Column(DateTime, default=func.current_timestamp())

    def __init__(self):
        return


class Transaction(Base):
    __tablename__ = 'transaction'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(UUID, default=uuid.uuid4, index=True)
    date = Column(DateTime, default=func.current_timestamp())
    status = Column(String, nullable=False)  # completed, cancelled, revised
    amount = Column(Float, nullable=False)
    receiver_id = Column(Integer, ForeignKey(Client.id), nullable=False)
    sender_id = Column(Integer, ForeignKey(Client.id), nullable=True),
    CheckConstraint(amount > 0, name="positive_check")

    def __init__(self, amount: float, status: str, receiver_id: int, sender_id: int):
        self.amount = amount
        self.status = status
        self.receiver_id = receiver_id
        self.sender_id = sender_id


Base.metadata.create_all(engine)
