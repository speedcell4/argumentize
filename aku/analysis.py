import argparse
import functools
import inspect
import sys
from typing import Callable

from aku.arguments import add_function


class Aku(object):
    def __init__(self) -> None:
        super(Aku, self).__init__()
        self.parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        self.functions = {}

    def register(self, func: Callable, name: str = None) -> Callable:
        if name is None:
            name = func.__name__
        assert name not in self.functions

        self.functions[name] = func
        return func

    def run(self, args=None, namespace=None):
        slots = []
        if self.functions.__len__() == 1:
            func = list(self.functions.values())[0]
            add_function(self.parser, self.parser, func, slots=slots)
        else:
            subparsers = self.parser.add_subparsers()
            parsers = {
                name: subparsers.add_parser(name)
                for name, _ in self.functions.items()
            }
            if sys.argv.__len__() > 1 and sys.argv[1] in parsers:
                func = self.functions[sys.argv[1]]
                add_function(parsers[sys.argv[1]], parsers[sys.argv[1]], func, slots=slots)

        namespace, args = self.parser.parse_known_args(args=args, namespace=namespace)
        kwargs = vars(self.parser.parse_args(args=args, namespace=namespace))

        keep = inspect.getfullargspec(func).varkw is not None

        for name, params in slots[::-1]:
            # tgt, src = zip(*params)
            kwargs[name] = functools.partial(
                kwargs[name], **{
                    t: kwargs[s] if keep else kwargs.pop(s)
                    for t, s in params
                }
            )
            if not keep:
                kwargs.pop(f'{name}_choose')

        return func(**kwargs)