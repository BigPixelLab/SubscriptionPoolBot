from __future__ import annotations

import inspect
import typing


class Slot:
    """ Слот для handler-ов, позволяет подключать функции,
        которые будут вызваны при вызове .emit() """

    def __init__(self, handlers: typing.Callable | list[typing.Callable] = None):
        self.handlers = []
        if hasattr(handlers, '__iter__'):
            self.handlers = list(handlers)
        elif handlers is not None:
            self.handlers = [handlers]

    def bind(self, handler, index=None) -> Slot:
        """ Добавляет функцию в список вызова """

        if index is not None:
            self.handlers.insert(index, handler)
            return self
        self.handlers.append(handler)
        return self

    async def emit(self, *args, **kwargs):
        """ Вызывает все зарегистрированные обработчики """

        for function in self.handlers:
            # noinspection PyTypeChecker
            await self.call(function, args, kwargs)
        return bool(self.handlers)

    @classmethod
    async def call(cls, function, args, kwargs):
        """ Правильно вызывает функцию с переданными параметрами, не зависимо
           от того обычная ли это функция, асинхронная или awaitable-объект """

        if inspect.iscoroutinefunction(function):
            await function(*args, **kwargs)
            return
        if callable(function):
            function(*args, **kwargs)
            return
        if args or kwargs:
            raise TypeError('No arguments can be provided to the awaitable')
        await function
