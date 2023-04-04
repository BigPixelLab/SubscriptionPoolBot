
def str2list(item_conv, sep=','):
    """ Возвращает converter, преобразующий строку в список """
    # if passed string - already converting.
    # Helpful for use like this:
    #   `ConvertBy[str2list]`
    if isinstance(item_conv, str):
        return item_conv.split(sep)
    return lambda x: list(map(item_conv, x.split(sep)))
