"""
EasyQuery lib.
"""
import typing

import peewee

QueryArgs = dict[str, typing.Any]
T = typing.TypeVar('T')
C = typing.TypeVar('C')

__default_db__: typing.Optional[peewee.Database] = None


def set_default_db(db: peewee.Database):
    global __default_db__
    __default_db__ = db


def get_default_db() -> typing.Optional[peewee.Database]:
    global __default_db__
    return __default_db__


def _execute(query: str, args: QueryArgs, db: peewee.Database = None) -> typing.Any:

    db = db or __default_db__
    if db is None:
        raise ValueError("Нет активного соединения с базой данных")

    return db.execute_sql(query, args)


def execute(query: str, args: QueryArgs, db: peewee.Database = None) -> None:
    """
    Выполняет запрос.
    Полезно, если запрос не возвращает данных.

    >>> execute(' DELETE FROM "Cats" ', {})
    """
    _execute(query, args, db)


def fetch_rows(query: str, args: QueryArgs, into: typing.Type[C] = list,
               db: peewee.Database = None) -> typing.Type[C][tuple]:
    """
    Выполняет запрос, и возвращает все полученные записи.
    Полезно, если из базы достаются произвольные значения.

    >>> fetch_rows(' SELECT "Cats".name AS cat, "Dogs".name AS dog FROM "Cats", "Dogs" ', {})
    [('Murka', 'Rex'), ('Murka', 'Muhtar'), ...]
    """
    return into(_execute(query, args, db))


def fetch_values(query: str, args: QueryArgs, into: typing.Type[C] = list,
                 db: peewee.Database = None) -> typing.Type[C][typing.Any]:
    """
    Выполняет запрос, и возвращает первое значение каждой из полученных записей.
    Полезно, если из базы достаются строки, в каждой из которых одно значение.

    >>> fetch_rows(' SELECT name FROM "Cats" ', {})
    ['Murka', 'Barsik', ...]
    """
    return into(row[0] for row in _execute(query, args, db))


# query: str, args: QueryArgs, db: peewee.Database = None
def fetch(model: typing.Type[T], query: str, args: QueryArgs, into: typing.Type[C] = list,
          db: peewee.Database = None) -> typing.Type[C][T]:
    # noinspection PyUnresolvedReferences
    """
    Выполняет запрос, и оборачивает каждую из записей результата в модель.
    Полезно, если из таблицы достаются все поля.

    >>> fetch(Cat, ' SELECT * FROM "Cats" ', {})
    [Cat(name='Murka', color='brown'), Cat(name='Barsik', color='black'), ...]
    """
    query_result = _execute(query, args, db)
    columns = (column[0] for column in query_result.description)
    return into(model(**dict(zip(columns, row))) for row in query_result)


def single_row(query: str, args: QueryArgs, db: peewee.Database = None) -> tuple:
    """
    Выполняет запрос, и достаёт запись.
    Полезно, если из базы достаются произвольные значения одной записи.

    >>> single_row(' SELECT "Cats".name AS cat, "Dogs".name AS dog FROM "Cats", "Dogs" LIMIT 1 ', {})
    ('Murka', 'Rex')
    """
    return next(_execute(query, args, db))


def single_value(query: str, args: QueryArgs, db: peewee.Database = None) -> typing.Any:
    """
    Выполняет запрос, достаёт запись и распаковывает хранящееся в ней значение.
    Полезно, если из запроса возвращается единственное значение.

    >>> single_value(' SELECT count(*) FROM "Cats" ', {})
    54321
    """
    value, = next(_execute(query, args, db))
    return value


def single(model: typing.Type[T], query: str, args: QueryArgs, db: peewee.Database = None) -> T:
    # noinspection PyUnresolvedReferences
    """
    Выполняет запрос, достаёт строку и оборачивает её в модель.
    Полезно, если из таблицы достаются все поля одной записи.

    >>> single(Cat, ' SELECT * FROM "Cats" LIMIT 1 ', {})
    Cat(name='Murka', color='brown')
    """
    query_result = _execute(query, args, db)
    columns = (column[0] for column in query_result.description)

    row = next(query_result)
    fields = dict(zip(columns, row))
    return model(**fields)
