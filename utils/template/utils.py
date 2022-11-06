from xml.dom import minidom

from .types_ import Context


def show_element(element: minidom.Element, context: Context):
    if attr := element.attributes.get('if'):
        return bool(eval(attr.value, {}, context))
    return True


def duplicate_elements_contexts(element: minidom.Element, context: Context):
    new_cvs_attr = element.attributes.get('for')
    if not new_cvs_attr:
        yield context
        return

    new_cvs = new_cvs_attr.value.split()

    context_var_attr = element.attributes.get('in')
    if not context_var_attr:
        raise ValueError('You must specify "in" attribute then specifying "for"')

    context_var = context[context_var_attr.value]

    for new_cvs_values in context_var:
        if len(new_cvs) == 1:
            new_cvs_values = [new_cvs_values]

        new_context = {**context}
        for cv, value in zip(new_cvs, new_cvs_values):
            new_context[cv] = value

        yield new_context


def mp(element: minidom.Element, o_tag: str, content: str, c_tag: str, *, padding_only: bool = False):
    ml = int(_ml.value) if (_ml := element.attributes.get('ml')) and not padding_only else 0
    mr = int(_mr.value) if (_mr := element.attributes.get('mr')) and not padding_only else 0
    pl = int(_pl.value) if (_pl := element.attributes.get('pl')) else 0
    pr = int(_pr.value) if (_pr := element.attributes.get('pr')) else 0
    return (' ' * ml) + o_tag + (' ' * pl) + content + (' ' * pr) + c_tag + (' ' * mr)
