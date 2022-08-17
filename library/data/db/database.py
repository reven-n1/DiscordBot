from typing import Optional, Union
from enum import Enum
import sqlalchemy
from library.data.data_loader import DataHandler
from sqlalchemy import Column, ForeignKey, Integer, Text, select
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio.engine import create_async_engine, AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.pool import NullPool

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


class aobject(object):
    """Inheriting this class allows you to define an async __init__.

    So you can create objects by doing something like `await MyClass(params)`
    """

    async def __new__(cls, *a, **kw):
        instance = super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self):
        pass


class Database(aobject):
    _instance: 'Database' = None

    async def __init__(self) -> None:
        self._config = DataHandler().get_database_config
        self.engine: AsyncEngine = create_async_engine(self.prepare_connection_string(self._config), poolclass=NullPool,
                                                       echo=False)
        self.connection = await self.engine.connect()
        self.metadata = metadata
        async with self.engine.begin() as conn:
            await conn.run_sync(self.metadata.create_all)

    async def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = await super(Database, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    async def get_class_session(cls) -> AsyncSession:
        return (await cls()).get_session()

    def get_session(self) -> AsyncSession:
        return sqlalchemy.orm.sessionmaker(bind=self.engine, class_=AsyncSession)()

    async def insert_if_not_exsits(self, table, *data):
        async with self.get_session() as session:
            result = (await session.execute(select(table).where(*data))).scalars().first()
            if not result:
                await session.merge(table(**{exp.left.name: exp.right.value for exp in data}))
                await session.commit()
            return (await session.execute(select(table).where(*data))).scalars().first() if not result else result

    async def get_statistic(self, parameter_name: Union[str, Statistic.Parameter]) -> Statistic:
        if isinstance(parameter_name, Statistic.Parameter):
            parameter_name = parameter_name.value
        return await self.insert_if_not_exsits(Statistic, Statistic.parameter_name == parameter_name)

    async def get_user_statistic(self, user_id, parameter_name: Union[str, StatisticParameter.Parameter],
                                 force_session: Optional[AsyncSession] = None):
        if not force_session:
            session = self.get_session()
        else:
            session = force_session
        if isinstance(parameter_name, StatisticParameter.Parameter):
            parameter_name = parameter_name.value
        result = (await session.execute(
            select(UsersStatisticCounter).join(StatisticParameter).where(UsersStatisticCounter.user_id == user_id,
                                                                         StatisticParameter.name == parameter_name))).scalars().first()
        if not result:
            parameter = await self.insert_if_not_exsits(StatisticParameter, StatisticParameter.name == parameter_name)
            result = await self.insert_if_not_exsits(UsersStatisticCounter, UsersStatisticCounter.user_id == user_id,
                                                     UsersStatisticCounter.parameter_id == parameter.id)
            await session.commit()
        if not force_session:
            await session.close()
        return result

    async def increment_user_statistic(self, user_id, parameter_name: Union[str, Statistic.Parameter]):
        async with self.get_session() as session:
            statistic = await self.get_user_statistic(user_id, parameter_name, session)
            statistic.count += 1
            session.add(statistic)
            await session.commit()

    async def reset_user_statistic(self, user_id, parameter_name: Union[str, Statistic.Parameter]):
        async with self.get_session() as session:
            statistic = await self.get_user_statistic(user_id, parameter_name, session)
            statistic.count = 0
            session.add(statistic)
            await session.commit()

    async def increment_statistic(self, parameter_name: Union[str, Statistic.Parameter]):
        """
        Increments the statistic with the given name.
        :param parameter_name: The name of the statistic to increment.
        :return: The new value of the statistic.
        """
        async with self.get_session() as session:
            statistic = await self.get_statistic(parameter_name)
            statistic.value += 1
            session.add(statistic)
            await session.commit()

    @staticmethod
    def prepare_connection_string(config: dict):
        """
        Prepares the connection string for the database.
        :param config: The config dictionary.
        :return: The connection string.
        """
        user = config.get('user') or ''
        password = config.get('password') or ''
        host = config.get('host')
        port = config.get('port') or ''
        database = config.get('database') or ''
        engine = config.get('engine')
        return f'{engine}://{user}{":" if user and password else ""}{password}{"@" if user and password else ""}{host}{":" if port else ""}{port}{"/" if database else ""}{database}'
