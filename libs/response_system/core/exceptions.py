from .responses import feedback, Response, no_response


class UserFriendlyException(Exception):
    """ Базовый класс для исключений, которые должны быть обработаны в user-friendly манере """

    def __init__(self, description: str):
        self._description = description

    @property
    def description(self) -> str:
        return self._description

    def response(self) -> Response:
        if not self._description:
            return no_response()
        return feedback(self._description)
