import abc
import functools
from typing import Callable, Any, Optional, Generator, Iterable, Union, Literal, NoReturn
from xml.dom.minidom import Element

from .exceptions import *


class ReadOnlyDict(dict):
    def __readonly__(self, *args, **kwargs):
        raise RuntimeError("Cannot modify ReadOnlyDict")
    __setitem__ = __readonly__
    __delitem__ = __readonly__
    pop = __readonly__
    popitem = __readonly__
    clear = __readonly__
    update = __readonly__
    setdefault = __readonly__
    del __readonly__


class TokenSet(list):
    pass


SendNothing = object()


class HandlerWrapper:
    def __init__(self, handler: Callable, annotations: dict, defaults: dict):
        self.handler = handler
        self.annotations = annotations
        self.defaults = defaults

    def __call__(self, tag: 'Tag', arguments: dict[str, tuple[str, Callable]]) -> Any:
        provided = set(arguments.keys())
        annotated = set(self.annotations.keys())

        send_remaining = '__rem' in annotated
        annotated -= {'__rem'}

        mandatory = annotated - set(self.defaults.keys())

        if unprovided := mandatory - provided:
            raise ParsingError(f'{tag.element.tagName}: Arguments {unprovided} were expected, but not provided')
        if not send_remaining and (unexpected := provided - annotated):
            raise ParsingError(f'{tag.element.tagName}: Got unexpected arguments {unexpected}')

        args = {}
        for arg in provided.intersection(annotated):
            value, convert = arguments[arg]
            args[arg] = convert(value, tag.context, self.annotations[arg])
        defs = {arg: self.defaults[arg] for arg in annotated - provided}

        if not send_remaining:
            return self.handler(tag, **args, **defs)

        remaining = {}
        for arg in provided - annotated:
            value, convert = arguments[arg]
            remaining[arg] = convert(value, tag.context, str)

        return self.handler(tag, **args, **defs, __rem=remaining)


class Parser:
    SKIP_ANNOTATIONS = ['return', 'tag']
    """ Entries to skip in handler annotations """

    __handler_wrapper_class__ = HandlerWrapper

    def __init__(self):
        self.handlers: dict = {}
        self.text_handler: Optional[Callable] = None

    def __parse__(self) -> Generator[Any, Any, None]:
        while (yield) is not None:
            pass
        yield None

    def __error__(self, error, comment) -> NoReturn:
        raise error(f'{self.__class__.__name__}: {comment}')

    def parse(self, element: Element, context: dict):
        pc = ParsingContext(self, self.__parse__())
        return pc.parse(element, ReadOnlyDict(context))

    def _register(self, func, name: str = None, override: bool = False,
                  annotations: dict = None, defaults: dict = None):

        # Получаем имя тега
        if name is None:
            name = getattr(func, '__name__', None)
        if name is None:
            self.__error__(HandlerRegistrationError, 'Cannot extract tag name, provide name explicitly')
        if name in self.handlers and not override:
            self.__error__(HandlerRegistrationError, f'Handler with name "{name}" already registered')

        # Получаем аннотации типов
        if not annotations:
            annotations = getattr(func, '__annotations__', None)
        if annotations is None:
            self.__error__(HandlerRegistrationError, f'({name}) Cannot extract annotations, provide annotations '
                                                     f'explicitly')

        annotations = annotations.copy()
        for skip in self.SKIP_ANNOTATIONS:
            annotations.pop(skip, None)

        # Получаем значения по-умолчанию
        if not defaults:
            defaults = getattr(func, '__kwdefaults__', None)
        if not defaults and getattr(func, '__defaults__', None):
            self.__error__(HandlerRegistrationError, 'Cannot properly extract defaults. Try making arguments kw-only, '
                                                     'ex.: def handler(tag: Tag, *, arg1, arg2=5)')
        defaults = defaults or {}

        if unexpected := set(defaults.keys()) - set(annotations.keys()):
            self.__error__(HandlerRegistrationError, f'You cannot provide defaults to unlisted arguments: {unexpected}')

        self.handlers[name] = self.__handler_wrapper_class__(func, annotations, defaults)
        return func

    def register(self, func=None, /, name: str = None, override: bool = False,
                 annotations: dict = None, defaults: dict = None) -> Callable:
        """
        Регистрирует обработчик тега. Данный обработчик будет вызываться для элементов с указанным
        именем тега

        :param func: Обработчик тега, ответственен за преобразование Element-ов в принимаемые
            parser-ом данные
        :param name: Имя тега как оно будет встречаться в шаблоне. Если не указано, будет
            автоматически извлечено из имени функции
        :param override: Если перезаписывается существующий обработчик, это должно быть явно указано
            с помощью данного аргумента
        :param annotations: Аргументы, используемые тегом, с указанием их типов. Если не указано,
            будет автоматически извлечено из __annotations__
        :param defaults: Значения по умолчанию для аргументов обработчика. Если не указано,
            будет автоматически извлечено из __kwdefaults__
        :return: ...
        """

        if func is None:
            return functools.partial(self._register, name, override, annotations, defaults)
        return self._register(func, name, override, annotations, defaults)

    def register_text(self, func=None):
        """
        Регистрирует текстовый обработчик. Данный обработчик будет вызываться для каждого xml элемента
        с типом TEXT_ELEMENT

        :param func:
        :return:
        """

        if self.text_handler:
            self.__error__(HandlerRegistrationError, 'There is already a text handler')

        self.text_handler = func
        return func


def register(parsers: Iterable[Parser], name: str = None, override: bool = False,
             annotations: dict = None, defaults: dict = None) -> Callable:
    def decorator(func):
        for parser in parsers:
            parser.register(
                func,
                name=name,
                override=override,
                annotations=annotations,
                defaults=defaults
            )
        return func
    return decorator


class AbstractParsingContext(abc.ABC):

    @abc.abstractmethod
    def parse(self, root: Element, context: ReadOnlyDict):
        raise NotImplementedError

    @abc.abstractmethod
    def process(self, element: Element, context: ReadOnlyDict):
        raise NotImplementedError

    @abc.abstractmethod
    def send(self, part: Any):
        raise NotImplementedError


class ConvertBy:
    class _Convert:
        __slots__ = ('convert',)

        def __init__(self, func):
            self.convert: Callable = func

    def __class_getitem__(cls, function: Callable) -> _Convert:
        return cls._Convert(function)


def converting_specifier(value, _, target_type) -> Any:
    """ Конвертирует переданную строку в указанный тип. Использует таблицу,
        для сопоставления типа с конвертером. Можно указать сторонний конвертер
        передав в качестве target_type значение ConvertBy[converter], где
        converter - конвертирующая функция """

    # noinspection PyProtectedMember
    if isinstance(target_type, ConvertBy._Convert):
        return target_type.convert(value)

    try:
        converter = converters[target_type]
    except KeyError:
        raise ParsingError(f'There is no converter for "{target_type}" (type={type(target_type)})')

    return converter(value)


def f_converting_specifier(value, context, target_type) -> Any:
    """ Конвертирует переданную строку в указанный тип, предварительно форматируя
        используя контекст. Использует таблицу, для сопоставления типа с
        конвертером. Можно указать сторонний конвертер передав в качестве
        target_type значение ConvertBy[converter], где converter - конвертирующая функция """

    return converting_specifier(value.format_map(context), context, target_type)


def context_var_specifier(value, context, _) -> Any:
    try:
        return context[value]
    except KeyError:
        raise NoContextVarError(f'Context variable "{value}" expected, but not provided')


def exec_python_specifier(value, context, _) -> Any:
    return eval(value, context, {})


converters = {
    bool: lambda x: {'True': True, 'False': False}[x],
    float: float,
    int: int,
    str: str,
}

specifiers = {
    '': f_converting_specifier,
    'nf': converting_specifier,
    'cv': context_var_specifier,
    'py': exec_python_specifier,
}


class ParsingContext(AbstractParsingContext):
    def __init__(self, parser: Parser, coroutine: Generator):
        self.coroutine = coroutine
        self.parser = parser

    def __display__(self, element: Element, context: ReadOnlyDict) -> bool:
        """ Возвращает True, если элемент должен быть отображён """
        attr = element.attributes.get('if', None)
        if attr is None:
            return True

        result = eval(attr.value, context, {})
        return bool(result)

    def __duplicate__(self, element: Element, context: ReadOnlyDict) -> Union[Iterable[ReadOnlyDict], Literal[False]]:
        """ Возвращает список контекстов, каждый из которых будет передан
            в свой дубликат элемента, или False если дублировать элемент
            не требуется """

        attr = element.attributes.get('for', None)
        if attr is None:
            return False

        # Используем пробелы, иначе "in" может быть частью слова
        cvs, *source_cv = attr.value.split(' in ', maxsplit=1)
        if not source_cv:
            self.__error__(ParsingError, 'Value of the "for" argument must contain "in" in it',
                           tag_name=element.tagName)
        source_cv = source_cv[0].strip()
        source = eval(source_cv, {}, context)

        # 'a, b , c' -> ['a', 'b', 'c']
        cvs = list(map(lambda x: x.strip(), cvs.split(',')))

        if len(cvs) == 1:
            cv, = cvs
            return [
                ReadOnlyDict(**context, **{cv: val})
                for val in source
            ]
        if len(cvs) > 1:
            return [
                ReadOnlyDict(**context, **{cv: v for cv, v in zip(cvs, val)})
                for val in source
            ]

        self.__error__(ParsingError, f'List of the variables to unpack to cannot be empty',
                       tag_name=element.tagName)

    def __arguments__(self, element: Element, skip: set[str] = None) -> dict[str, tuple[str, Callable]]:
        """ Извлекает аргументы и их конвертеры """
        skip = skip or set()
        arguments = {}

        for attribute, value in element.attributes.items():
            if attribute in skip:
                continue

            attribute, *spec = attribute.split('.', maxsplit=1)
            spec = spec[0] if spec else ''

            converter = None
            if spec is not None:
                converter = specifiers.get(spec, None)
            if spec is not None and converter is None:
                self.__error__(ParsingError, f'No such specifier as "{spec}" is registered',
                               tag_name=element.tagName)

            if attribute in arguments:
                self.__error__(ParsingError, f'Argument "{attribute}" is passed multiple times',
                               tag_name=element.tagName)

            arguments[attribute] = value, converter

        return arguments

    def __handler__(self, handler: Callable, element: Element, context: ReadOnlyDict):
        """ ... """
        tag = Tag(self, element, context)
        result = handler(tag, self.__arguments__(element, skip={'for', 'if'}))
        if result is SendNothing:
            return
        self.send(result)

    def __error__(self, error, comment, tag_name=None) -> NoReturn:
        """ Формирует и вызывает переданную ошибку """
        if tag_name is not None:
            raise error(f'{self.parser.__class__.__name__} ({tag_name}): {comment}')
        raise error(f'{self.parser.__class__.__name__}: {comment}')

    def parse(self, root: Element, context: ReadOnlyDict):
        next(self.coroutine)  # Initialization
        for element in root.childNodes:
            self.process(element, context)
        return next(self.coroutine)  # Finishing up

    def process(self, element: Element, context: ReadOnlyDict):

        if element.nodeType == Element.TEXT_NODE and self.parser.text_handler:
            tag = Tag(self, element, context)
            result = self.parser.text_handler(tag)
            self.send(result)
            return

        if element.nodeType != Element.ELEMENT_NODE:
            return

        if not self.__display__(element, context):
            return

        handler = self.parser.handlers.get(element.tagName, None)

        if handler is None:
            self.__error__(ParsingError, f'Got unexpected tag "{element.tagName}"')

        duplicate = self.__duplicate__(element, context)

        if duplicate is False:  # Не указано дублирование - быстрый путь
            self.__handler__(handler, element, context)
            return

        for child_context in duplicate:
            self.__handler__(handler, element, child_context)

    def send(self, part: Any):
        if not isinstance(part, TokenSet):
            self.coroutine.send(part)
            return
        for single_part in part:
            self.coroutine.send(single_part)


class Tag:
    def __init__(self, pc: ParsingContext, element: Element, context: ReadOnlyDict):
        self._element = element
        self._context = context
        self._pc = pc

    @property
    def element(self):
        return self._element

    @property
    def context(self):
        return self._context

    def process(self, element: Element, context: dict = None):
        if context and not isinstance(context, ReadOnlyDict):
            context = ReadOnlyDict(context)
        return self._pc.process(element, context or self._context)

    def send(self, part: Any):
        return self._pc.send(part)


__all__ = (
    'ReadOnlyDict',
    'TokenSet',
    'SendNothing',
    'HandlerWrapper',
    'Parser',
    'register',
    'AbstractParsingContext',
    'ConvertBy',
    'converting_specifier',
    'f_converting_specifier',
    'context_var_specifier',
    'exec_python_specifier',
    'converters',
    'specifiers',
    'ParsingContext',
    'Tag'
)
