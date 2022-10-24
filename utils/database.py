from __future__ import annotations

import logging
from contextlib import suppress
from typing import Any, TypeVar, Type

import psycopg2
import psycopg2.extras
from psycopg2.extras import DictRow

import settings

logger = logging.getLogger(__name__)
T = TypeVar('T')


class ConnectionManager:
    _connection: psycopg2.connection = None

    def __init__(self, cursor_factory=None):
        self._cursor: psycopg2.cursor | None = None
        self._factory = cursor_factory

    def __enter__(self) -> psycopg2.cursor:
        if self._connection is None or self._connection.closed:
            self._reconnect()
        self._cursor = self._connection.cursor(cursor_factory=self._factory)
        return self._cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        with suppress(psycopg2.Error):
            if exc_type is None:
                self._connection.commit()
            else:
                self._connection.rollback()
        with suppress(psycopg2.Error):
            self._cursor.close()

    @classmethod
    def _reconnect(cls):
        while True:
            try:
                cls._connection = psycopg2.connect(settings.DATABASE_URI)
                return
            except psycopg2.Error as error:
                logger.error(error)
            logger.warning('Retrying to connect to the database..')

    @classmethod
    def close_connection(cls):
        if cls._connection is not None and not cls._connection.closed:
            cls._connection.close()


def _fetch(factory: Type[psycopg2.cursor], query: str, kwargs: dict, comment: str | None) -> list[DictRow]:
    while True:
        with suppress(psycopg2.OperationalError), ConnectionManager(factory) as cursor:
            logger.info(comment if comment is not None else 'Executing database query..')
            cursor.execute(query, kwargs)
            records = cursor.fetchall()
            break
    return records


def fetch_rows(query: str, __comment: str = None, /, **kwargs: Any) -> list[DictRow]:
    """Returns list of rows as DictRows"""
    return _fetch(psycopg2.extras.DictCursor, query, kwargs, __comment)


def fetch_values(query: str, __comment: str = None, /, **kwargs: Any) -> list[Any]:
    """Returns list of single values"""
    return [row[0] for row in _fetch(psycopg2.extras.DictCursor, query, kwargs, __comment)]


def fetch(record_class: Type[T], query: str, __comment: str = None, /, **kwargs: Any) -> list[T]:
    """Returns list of objects of given type"""
    records = _fetch(psycopg2.extras.DictCursor, query, kwargs, __comment)
    return [record_class(**record) for record in records]


def _single(factory: Type[psycopg2.cursor], query: str, kwargs: dict, comment: str | None) -> DictRow:
    while True:
        with suppress(psycopg2.OperationalError), ConnectionManager(factory) as cursor:
            logger.info(comment if comment is not None else 'Executing database query..')
            cursor.execute(query, kwargs)
            record = cursor.fetchone()
            break
    return record


def single_row(query: str, __comment: str = None, /, **kwargs: Any) -> DictRow:
    """Returns single row as DictRow"""
    return _single(psycopg2.extras.DictCursor, query, kwargs, __comment)


def single_value(query: str, __comment: str = None, /, **kwargs: Any) -> Any:
    """Returns single value"""
    record = _single(psycopg2.extras.DictCursor, query, kwargs, __comment)
    if record is None or len(record) == 0:
        return None
    return record[0]


def single(record_class: Type[T], query: str, __comment: str = None, /, **kwargs: Any) -> T:
    """Returns single row as given type"""
    record: DictRow | None = _single(psycopg2.extras.DictCursor, query, kwargs, __comment)
    if record is None:
        return None
    return record_class(**record)


def execute(query: str, __comment: str = None, /, **kwargs: Any):
    while True:
        with suppress(psycopg2.OperationalError), ConnectionManager() as cursor:
            logger.info(__comment if __comment is not None else 'Executing database query..')
            cursor.execute(query, kwargs)
            break
