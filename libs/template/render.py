from pathlib import Path
from typing import Optional
from xml.dom import minidom

from .types import Parser, ReadOnlyDict

__default_syntax__: Optional[Parser] = None
__global_context__: dict = {}


def set_default_syntax(syntax: Parser):
    global __default_syntax__
    __default_syntax__ = syntax


def get_default_syntax() -> Parser:
    return __default_syntax__


def set_global_context(context: dict):
    global __global_context__
    __global_context__ = context


def get_global_context() -> dict:
    return __global_context__


def render_document(document: minidom.Document, context: dict, path: str = None, syntax: Parser = None):
    syntax = syntax or __default_syntax__
    if syntax is None:
        raise ValueError('No default syntax is set, so it must be provided manually')

    _context = __global_context__.copy()
    if path:
        path = Path(path)
        _context.update(TDIR=path.parent, TFILE=path)
    _context.update(context)

    # noinspection PyTypeChecker
    return syntax.parse(document, ReadOnlyDict(_context))


def render_string(string: str, context: dict, syntax: Parser = None):
    return render_document(
        minidom.parseString(string),
        context,
        syntax=syntax
    )


def render(path: str, context: dict, syntax: Parser = None):
    return render_document(
        minidom.parse(path),
        context,
        path=path,
        syntax=syntax
    )


__all__ = (
    'set_default_syntax',
    'get_default_syntax',
    'set_global_context',
    'get_global_context',
    'render_document',
    'render_string',
    'render'
)
