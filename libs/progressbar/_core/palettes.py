
PaletteType = tuple[str, ...]

RED_PALETTE: PaletteType = ('🟥', )
ORANGE_PALETTE: PaletteType = ('🟧', )
YELLOW_PALETTE: PaletteType = ('🟨', )
GREEN_PALETTE: PaletteType = ('🟩', )
BLUE_PALETTE: PaletteType = ('🟦', )
PURPLE_PALETTE: PaletteType = ('🟪', )
BROWN_PALETTE: PaletteType = ('🟫', )
BLACK_PALETTE: PaletteType = ('⬛', )
WHITE_PALETTE: PaletteType = ('⬜', )
RAINBOW_PALETTE: PaletteType = ('🟥', '🟧', '🟨', '🟩', '🟦', '🟪')

BUILTIN_PALETTE_MAP: dict[str, PaletteType] = {
    'red': RED_PALETTE,
    'orange': ORANGE_PALETTE,
    'yellow': YELLOW_PALETTE,
    'green': GREEN_PALETTE,
    'blue': BLUE_PALETTE,
    'purple': PURPLE_PALETTE,
    'brown': BROWN_PALETTE,
    'black': BLACK_PALETTE,
    'white': WHITE_PALETTE,
    'rainbow': RAINBOW_PALETTE,
}
