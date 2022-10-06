from Levenshtein import ratio

import settings
from . import models


def transliterate(text: str) -> str:
    """ Transliterates text using given table """
    table = settings.DEFAULT_TRANSLITERATION_TABLE
    return ''.join(
        table.get(letter, letter)
        for letter in text.lower()
    )


def get_suggested_service(request: str, services: list[models.Service]) -> tuple[models.Service, float]:
    service = max(services, key=lambda s: ratio(request, s.name))
    return service, ratio(request, service.name)
