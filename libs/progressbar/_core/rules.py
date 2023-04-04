import typing as _t

RuleType = _t.Callable[[tuple[str, ...], int, int, int], str]


def rule_repeat(palette: tuple[str, ...], start: int, end: int, _: int) -> str:
    """
    [123412341___]
    """
    length = len(palette)
    return ''.join(
        palette[i % length]
        for i in range(start, end)
    )


def rule_reverse(palette: tuple[str, ...], start: int, end: int, _: int) -> str:
    """
    [123432123___]
    """
    length = len(palette) - 1  # -1, иначе индекс будет выходить за пределы массива
    if not length:
        return rule_single(palette, start, end, _)
    return ''.join(
        palette[abs((i - length) % (2 * length) - length)]
        for i in range(start, end)
    )


def rule_single(palette: tuple[str, ...], start: int, end: int, _: int) -> str:
    """
    [111111111___]
    """
    return ''.join(
        palette[0]
        for _ in range(start, end)
    )


def rule_charge(palette: tuple[str, ...], start: int, end: int, width: int) -> str:
    """
    [111_________]
    [222222______]
    [333333333___]
    [444444444444]
    """
    length = len(palette)
    return ''.join(
        palette[min(length - 1, length * (end - start) // width)]
        for _ in range(start, end)
    )


def rule_stick(palette: tuple[str, ...], start: int, end: int, _: int) -> str:
    """
    [34__________]
    [111234______]
    """
    length = len(palette)
    return ''.join(
        palette[max(0, i + length - end)]
        for i in range(start, end)
    )


BUILTIN_RULE_MAP: dict[str, RuleType] = {
    'repeat': rule_repeat,
    'reverse': rule_reverse,
    'single': rule_single,
    'charge': rule_charge,
    'stick': rule_stick
}
