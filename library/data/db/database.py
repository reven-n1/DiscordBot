from typing import Union
from enum import Enum
import sqlalchemy
from library.data.data_loader import DataHandler
from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Statistic(Base):
    __tablename__ = 'statistic'

    parameter_name = Column(Text, primary_key=True)
    value = Column(Integer, default=0)

    class Parameter(Enum):
        ARK = 'ark'
        GER_BOT = 'ger_bot'
        GER_ME = 'ger_me'
        GER = 'ger'
        SELF_GER = 'self_ger'


class StatisticParameter(Base):
    __tablename__ = 'statistic_parameters'

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)

    class Parameter(Enum):
        SIX_MISS = 'six_miss'
        GER_HIT = 'ger_hit'
        GER_USE = 'ger_use'


class UsersArkCollection(Base):
    __tablename__ = 'users_ark_collection'

    user_id = Column(Text, primary_key=True)
    operator_name = Column(Text, primary_key=True)
    rarity = Column(Integer)
    operator_count = Column(Integer, default=0)

    def __repr__(self) -> str:
        return f'{self.user_id} {self.operator_name} {self.rarity} {self.operator_count}'


class UsersStatisticCounter(Base):
    __tablename__ = 'users_statistic_counter'

    user_id = Column(Text, primary_key=True)
    parameter_id = Column(ForeignKey('statistic_parameters.id'), primary_key=True, index=True)
    count = Column(Integer, default=0)

    parameter = relationship('StatisticParameter')

    def __repr__(self) -> str:
        return f'{self.user_id} {self.parameter_id} {self.count}'


class Database(object):
    _instance: 'Database' = None

    def __init__(self) -> None:
        self._config = DataHandler().get_database_config
        self.engine = sqlalchemy.create_engine(self.prepare_connection_string(self._config), echo=False)
        self.connection = self.engine.connect()
        self.metadata = metadata
        self.metadata.create_all(self.engine)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Database, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def get_instance(cls) -> 'Database':
        if not getattr(cls, '_instance', None):
            cls._instance = cls()
        return cls._instance

    def get_session(self) -> sqlalchemy.orm.session.Session:
        return sqlalchemy.orm.sessionmaker(bind=self.engine)()

    def insert_if_not_exsits(self, table, **data):
        with self.get_session() as session:
            result = session.query(table).filter_by(**data).first()
            if not result:
                session.merge(table(**data))
                session.commit()
            return session.query(table).filter_by(**data).first() if not result else result

    def get_statistic(self, parameter_name: Union[str, Statistic.Parameter]) -> Statistic:
        if isinstance(parameter_name, Statistic.Parameter):
            parameter_name = parameter_name.value
        return self.insert_if_not_exsits(Statistic, parameter_name=parameter_name)

    def get_user_statistic(self, user_id, parameter_name: Union[str, StatisticParameter.Parameter], force_session=None):
        if not force_session:
            session = self.get_session()
        else:
            session = force_session
        if isinstance(parameter_name, StatisticParameter.Parameter):
            parameter_name = parameter_name.value
        result = session.query(UsersStatisticCounter).join(StatisticParameter).filter(UsersStatisticCounter.user_id == user_id, StatisticParameter.name == parameter_name).first()
        if not result:
            parameter = self.insert_if_not_exsits(StatisticParameter, name=parameter_name)
            result = self.insert_if_not_exsits(UsersStatisticCounter, user_id=user_id, parameter_id=parameter.id)
            session.commit()
        if not force_session:
            session.close()
        return result

    def increment_user_statistic(self, user_id, parameter_name: Union[str, Statistic.Parameter]):
        with self.get_session() as session:
            statistic = self.get_user_statistic(user_id, parameter_name, session)
            statistic.count += 1
            session.add(statistic)
            session.commit()

    def reset_user_statistic(self, user_id, parameter_name: Union[str, Statistic.Parameter]):
        with self.get_session() as session:
            statistic = self.get_user_statistic(user_id, parameter_name, session)
            statistic.count = 0
            session.add(statistic)
            session.commit()

    def increment_statistic(self, parameter_name: Union[str, Statistic.Parameter]):
        with self.get_session() as session:
            statistic = self.get_statistic(parameter_name)
            statistic.value += 1
            session.add(statistic)
            session.commit()

    @staticmethod
    def prepare_connection_string(config: dict):
        user = config.get('user') or ''
        password = config.get('password') or ''
        host = config.get('host')
        port = config.get('port') or ''
        database = config.get('database') or ''
        engine = config.get('engine')
        return f'{engine}:///{user}{":" if user and password else ""}{password}{"@" if user and password else ""}{host}{":" if port else ""}{port}{"/" if database else ""}{database}'
