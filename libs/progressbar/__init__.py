# noinspection PyUnresolvedReferences
"""
BASIC USAGE:
>>> import progressbar
>>> progressbar.progressbar(4 / 5)
'[⬛⬛⬛⬛⬛⬛⬛⬛⬜⬜]'
>>> progressbar.progressbar(0.5)
'[⬛⬛⬛⬛⬛⬜⬜⬜⬜⬜]'
>>> progressbar.progressbar(4 / 5, width=5)
'[⬛⬛⬛⬛⬜]'
"""

# Submodules
from ._modules import styles

# Types
from ._core.rules import RuleType
from ._core.palettes import PaletteType
from ._core.style import Style

# Main stuff
from ._core.progressbar import *
