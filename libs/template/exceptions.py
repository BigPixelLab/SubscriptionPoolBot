
class TemplateModuleError(Exception):
    pass


class HandlerRegistrationError(TemplateModuleError):
    pass


class ParsingError(TemplateModuleError):
    pass


class NoContextVarError(TemplateModuleError):
    pass


__all__ = (
    'TemplateModuleError',
    'HandlerRegistrationError',
    'ParsingError',
    'NoContextVarError',
)
