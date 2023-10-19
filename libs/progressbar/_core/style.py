import typing as _t

from .palettes import BUILTIN_PALETTE_MAP,  PaletteType
from .rules import BUILTIN_RULE_MAP, RuleType, rule_repeat

default_border_left: str = '['
default_border_right: str = ']'
default_rule: RuleType = rule_repeat


class Style:
    def __init__(self, **kwargs):
        """
        Style class for progressbar.

        Allowed arguments:
         * foreground: PaletteType | str - Foreground palette;
         * background: PaletteType | str - Background palette;
         * border_left: str - Symbol for left border;
         * border_right: str - Symbol for right border;
         * border: tuple[str, str] | str - Shortcut to set both borders at once;
         * rule_foreground: RuleType | str - Rule function which renders foreground based on palette;
         * rule_background: RuleType | str - Rule function which renders background based on palette;
         * rule: RuleType | str - Shortcut to set same rule for both foreground and background.
         * mark: str - Target mark
         * mark_reached: str - Target mark reached
        """
        attrs = self._resolve_attributes(**kwargs)
        self._foreground = attrs['foreground']
        self._background = attrs['background']
        self._border_left = attrs['border_left']
        self._border_right = attrs['border_right']
        self._rule_foreground = attrs['rule_foreground']
        self._rule_background = attrs['rule_background']
        self._mark = attrs['mark']
        self._mark_reached = attrs['mark_reached']

    @classmethod
    def _resolve_attributes(
            cls,
            foreground: _t.Union[PaletteType, str],
            background: _t.Union[PaletteType, str],
            border_left: str = None,
            border_right: str = None,
            border: _t.Union[tuple[str, str], str] = None,
            rule_foreground: _t.Union[RuleType, str] = None,
            rule_background: _t.Union[RuleType, str] = None,
            rule: _t.Union[RuleType, str] = None,
            mark: str = None,
            mark_reached: str = None
    ):

        # Palettes

        _foreground = cls._handle_attribute(
            foreground, BUILTIN_PALETTE_MAP,
            KeyError(f'No such built-in palette as {foreground}')
        )
        _background = cls._handle_attribute(
            background, BUILTIN_PALETTE_MAP,
            KeyError(f'No such built-in palette as {background}')
        )

        # Borders

        if border is not None and (border_left is not None or border_right is not None):
            raise ValueError('Shortcut attribute "border" cannot be set together '
                             'with its parts "border_left" or "border_right"')

        if border is not None and len(border) != 2:
            raise ValueError('Length of the border attribute must be exactly 2')

        _border_left = border_left
        _border_right = border_right

        if border is not None:
            _border_left, _border_right = border

        if _border_left is None:
            _border_left = default_border_left

        if _border_right is None:
            _border_right = default_border_right

        # Rules

        if rule is not None and (rule_foreground is not None or rule_background is not None):
            raise ValueError('Shortcut attribute "rule" cannot be set together '
                             'with its parts "foreground_rule" or "background_rule"')

        _rule_foreground = cls._handle_attribute(
            rule_foreground, BUILTIN_RULE_MAP,
            KeyError(f'No such built-in rule as {rule_foreground}')
        )
        _rule_background = cls._handle_attribute(
            rule_background, BUILTIN_RULE_MAP,
            KeyError(f'No such built-in rule as {rule_background}')
        )

        __rule = cls._handle_attribute(
            rule, BUILTIN_RULE_MAP,
            KeyError(f'No such built-in rule as {rule}')
        )

        if __rule is not None:
            _rule_foreground = _rule_background = __rule

        if _rule_foreground is None:
            _rule_foreground = default_rule

        if _rule_background is None:
            _rule_background = default_rule

        return {
            'foreground': _foreground,
            'background': _background,
            'border_left': _border_left,
            'border_right': _border_right,
            'rule_foreground': _rule_foreground,
            'rule_background': _rule_background,
            'mark': mark,
            'mark_reached': mark_reached
        }

    @classmethod
    def _handle_attribute(cls, attribute, mapping, exception):
        """ If attribute is a string, tries to get it from mapping and
            raises exception on failure, else returns attribute as is """
        try:
            if isinstance(attribute, str):
                return mapping[attribute]
        except KeyError:
            raise exception
        return attribute

    @property
    def foreground(self):
        return self._foreground

    @property
    def background(self):
        return self._background

    @property
    def border_left(self):
        return self._border_left

    @property
    def border_right(self):
        return self._border_right

    @property
    def border(self):
        return self._border_left, self._border_right

    @property
    def rule_foreground(self):
        return self._rule_foreground

    @property
    def rule_background(self):
        return self._rule_background

    @property
    def mark(self):
        return self._mark

    @property
    def mark_reached(self):
        return self._mark_reached

    def updated(self, **kwargs) -> 'Style':
        """ Creates new style based on this with made changes """
        self_attrs = {
            'border_left': self.border_left,
            'border_right': self.border_right,
            'rule_foreground': self.rule_foreground,
            'rule_background': self.rule_background,
            'mark': self.mark,
            'mark_reached': self.mark_reached
        }
        if 'foreground' not in kwargs:
            kwargs.update(foreground=self.foreground)
        if 'background' not in kwargs:
            kwargs.update(background=self.background)
        attrs = self._resolve_attributes(**kwargs)
        self_attrs.update(attrs)
        return Style(**self_attrs)
