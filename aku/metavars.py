from typing import Union

from aku.utils import is_optional, is_union, is_list


def render_type(retype) -> str:
    if is_optional(retype):
        args = render_type(Union[tuple(a for a in retype.__args__ if a is not type(None))])
        return f'{args}?'
    if is_union(retype):
        args = ', '.join(render_type(a) for a in retype.__args__)
        return f'{{{args}}}'
    if is_list(retype):
        args = render_type(retype.__args__[0])
        return f'[{args}]'

    return f'{retype.__name__}'.capitalize()
