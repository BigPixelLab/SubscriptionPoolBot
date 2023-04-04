from . import rules, palettes, style


basic_red = style.Style(
    foreground=palettes.RED_PALETTE,
    background=palettes.WHITE_PALETTE,
    border='[]',
    rule=rules.rule_single
)
basic_orange = basic_red.updated(foreground=palettes.ORANGE_PALETTE)
basic_yellow = basic_red.updated(foreground=palettes.YELLOW_PALETTE)
basic_green = basic_red.updated(foreground=palettes.GREEN_PALETTE)
basic_blue = basic_red.updated(foreground=palettes.BLUE_PALETTE)
basic_purple = basic_red.updated(foreground=palettes.PURPLE_PALETTE)
basic_brown = basic_red.updated(foreground=palettes.BROWN_PALETTE)
basic_black = basic_red.updated(foreground=palettes.BLACK_PALETTE)
basic_rainbow = basic_red.updated(foreground=palettes.RAINBOW_PALETTE)


__all__ = (
    'basic_red',
    'basic_orange',
    'basic_yellow',
    'basic_green',
    'basic_blue',
    'basic_purple',
    'basic_brown',
    'basic_black',
    'basic_rainbow',
)
