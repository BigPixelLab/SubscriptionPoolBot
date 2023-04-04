from .style import Style
from .styles import basic_green

default_size = 14
default_style = basic_green


def set_default_width(width: int):
    global default_size
    default_size = width


def get_default_width() -> int:
    return default_size


def set_default_style(style: Style):
    global default_style
    default_style = style


def get_default_style() -> Style:
    return default_style


def progressbar(ratio: float, width: int = None, style: Style = None) -> str:
    width = width if width is not None else default_size
    style = style if style is not None else default_style

    ratio = max(0., min(ratio, 1.))
    filled = int(ratio * width)

    foreground = style.rule_foreground(
        style.foreground, 0, filled, width
    ) if filled else ''
    background = style.rule_background(
        style.background, filled, width, width
    ) if width - filled else ''

    return style.border_left + foreground + background + style.border_right


class ProgressBar:
    def __init__(self, steps: int, width: int = None, style: Style = None):
        self._steps = steps
        self._completed_steps = 0
        self._width = width if width is not None else default_size
        self._style = style if style is not None else default_style

    def __iter__(self):
        return self

    def __next__(self):
        self.step()
        if self._completed_steps > self._steps:
            raise StopIteration
        return self.render()

    def __str__(self):
        return self.render()

    @property
    def steps(self):
        return self._steps

    @property
    def completed_steps(self):
        return self._completed_steps

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value: int):
        self._width = value

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value: Style):
        self._style = value

    def step(self, count: int = 1):
        self._completed_steps += count

    def reset(self):
        self._completed_steps = 0

    def render(self):
        return progressbar(self._completed_steps / self._steps, self._width, self._style)


__all__ = (
    'get_default_width',
    'set_default_width',
    'get_default_style',
    'set_default_style',
    'progressbar',
    'ProgressBar',
)
