""" ... """
import typing

VT = typing.TypeVar('VT')
ET = typing.TypeVar('ET')


# noinspection PyMissingOrEmptyDocstring
class Result(typing.Generic[VT, ET]):

    @property
    def is_ok(self) -> bool:
        raise NotImplementedError

    @property
    def is_error(self) -> bool:
        return not self.is_ok

    @property
    def value(self) -> VT:
        raise NotImplementedError

    @property
    def error(self) -> ET:
        raise NotImplementedError

    def unpack(self) -> VT:
        raise NotImplementedError


# noinspection PyMissingOrEmptyDocstring
class Ok(Result[VT, ET]):
    """ ... """

    def __init__(self, value: VT = None):
        self._value = value

    @property
    def is_ok(self) -> bool:
        return True

    @property
    def value(self) -> VT:
        return self._value

    @property
    def error(self) -> None:
        return None

    def unpack(self) -> VT:
        return self._value

    def __bool__(self):
        return True


# noinspection PyMissingOrEmptyDocstring
class Error(Result[VT, ET]):
    """ ... """

    def __init__(self, error: typing.Any = None):
        self._error = error

    @property
    def is_ok(self) -> bool:
        return False

    @property
    def value(self) -> None:
        return None

    @property
    def error(self) -> ET:
        return self._error

    def unpack(self) -> VT:
        raise ValueError(self._error)

    def __bool__(self):
        return False


__all__ = (
    'Result',
    'Error',
    'Ok'
)
