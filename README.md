# Aku

[![Actions Status](https://github.com/speedcell4/aku/workflows/unit-tests/badge.svg)](https://github.com/speedcell4/aku/actions)
[![PyPI version](https://badge.fury.io/py/aku.svg)](https://badge.fury.io/py/aku)
[![Downloads](https://pepy.tech/badge/aku)](https://pepy.tech/project/aku)

An interactive annotation-driven `ArgumentParser` generator

## Requirements

* Python 3.7 or higher

## Install

```shell script
python -m pip install aku --upgrade
```

## Type Annotations

* primitive types, 
    - e.g., `int`, `bool`, `str`, `float`, `Path`, etc.
* container types
    - list `List[T]` 
    - homogeneous tuple, e.g., `Tuple[T, ...]`
    - heterogeneous tuple, e.g., `Tuple[T1, T2, T3]`
    - literal, e.g., `Literal[42, 1905]`
* nested types
    - function, e.g., `Type[<func_name>]`
    - union of functions, e.g., `Union[Type[<func1_name>], Type[<func2_name>], Type[<func3_name>]]`

## Usage

### Primitive Types

The key idea of aku to generate `ArgumentParser` according to the type annotations of functions. For example, to register single function with only primitive types,

```python
from pathlib import Path

from aku import Aku

aku = Aku()


@aku.option
def foo(a: int, b: bool = True, c: str = '3', d: float = 4.0, e: Path = Path.home()):
    print(f'a => {a}')
    print(f'b => {b}')
    print(f'c => {c}')
    print(f'd => {d}')
    print(f'e => {e}')


aku.run()
```

`aku` will generate a `ArgumentParser` which provides your command line interface looks like below,

```shell script
~ python examples/foo.py --help 
usage: foo.py [-h] --a int [--b bool] [--c str] [--d float] [--e path]

optional arguments:
  -h, --help  show this help message and exit
  --a int     a
  --b bool    b (default: True)
  --c str     c (default: 3)
  --d float   d (default: 4.0)
  --e path    e (default: /Users/home)
```

Of course you can achieve the same functions by instantiating an `ArgumentParser`, but `aku` certainly makes such steps simple and efficient.

```python
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, SUPPRESS
from pathlib import Path


def tp_bool(arg_strings: str) -> bool:
    arg_strings = arg_strings.lower().strip()
    if arg_strings in ('t', 'true', 'y', 'yes', '1'):
        return True
    if arg_strings in ('f', 'false', 'n', 'no', '0'):
        return False
    raise ValueError


argument_parser = ArgumentParser(
    formatter_class=ArgumentDefaultsHelpFormatter,
)
argument_parser.add_argument('--a', type=int, metavar='int', default=SUPPRESS, required=True, help='a')
argument_parser.add_argument('--b', type=tp_bool, metavar='bool', default=True, help='b')
argument_parser.add_argument('--c', type=str, metavar='str', default='3', help='c')
argument_parser.add_argument('--d', type=float, metavar='float', default=4.0, help='d')
argument_parser.add_argument('--e', type=Path, metavar='path', default=Path.home(), help='e')

args = argument_parser.parse_args().__dict__
for key, value in args.items():
    print(f'{key} => {value}')
```

Moreover, if you register more than one functions, e.g., register function `add`,

```python
@aku.option
def add(x: int, y: int):
    print(f'{x} + {y} => {x + y}')
```

Then you can choose which one to run by passing its name as the first parameter,

```shell script
~ python examples/bar.py foo --help
usage: bar.py foo [-h] --a int [--b bool] [--c str] [--d float] [--e path]

optional arguments:
  -h, --help  show this help message and exit
  --a int     a
  --b bool    b (default: True)
  --c str     c (default: 3)
  --d float   d (default: 4.0)
  --e path    e (default: /Users/home)

~ python examples/bar.py add --help
usage: bar.py add [-h] --x int --y int

optional arguments:
  -h, --help  show this help message and exit
  --x int     x
  --y int     y

~ python examples/bar.py add --x 1 --y 2
1 + 2 => 3
```

### Container Types

```python
from typing import List, Tuple

from aku import Aku, Literal

aku = Aku()


@aku.option
def baz(a: List[int], b: Tuple[bool, ...], c: Tuple[int, bool, str], d: Literal[42, 1905]):
    print(f'a => {a}')
    print(f'b => {b}')
    print(f'c => {c}')
    print(f'd => {d}')


if __name__ == '__main__':
    aku.run()
```

* argument `a` is annotated with `List[int]`, thus every `--a` appends one item at the end of existing list
* homogenous tuple holds arbitrary number of elements with the same type, while heterogeneous tuple holds specialized number of elements with specialized type
* literal arguments can be assigned value from the specified ones

```shell script
~  python examples/baz.py --help                                                      
usage: baz.py [-h] --a [int] --b bool, ...) --c (int, bool, str --d int{1905, 42}

optional arguments:
  -h, --help            show this help message and exit
  --a [int]             a
  --b (bool, ...)       b
  --c (int, bool, str)  c
  --d int{1905, 42}     d

~ python examples/baz.py --a 1 --a 2 --a 3 --b "true,true,false,false,true" --c 42,true,"yes" --d 42
a => [1, 2, 3]
b => (True, True, False, False, True)
c => (42, True, 'yes')
d => 42

~ python examples/baz.py --a 1 --a 2 --a nice --b "true,wow" --c 42,true,"yes" --d 42
usage: baz.py [-h] [--a [int]] --b bool, ...) --c (int, bool, str --d int{1905, 42}
baz.py: error: argument --a: invalid int value: 'nice'

~ python examples/baz.py --a 1 --a 2 --a 3 --b "true,wow" --c 42,true,"yes" --d 42   
usage: baz.py [-h] [--a [int]] --b bool, ...) --c (int, bool, str --d int{1905, 42}
baz.py: error: argument --b: invalid fn value: 'true,wow'

~ python examples/baz.py --a 1 --a 2 --a 3 --b "true,true,false,false,true" --c 42,true,"yes,43" --d 42
usage: baz.py [-h] [--a [int]] [--b bool, ...)] --c (int, bool, str --d int{1905, 42}
baz.py: error: argument --c: invalid fn value: '42,true,yes,43'

~ python examples/baz.py --a 1 --a 2 --a 3 --b "true,true,false,false,true" --c 42,true,"yes" --d 43
usage: baz.py [-h] [--a [int]] [--b bool, ...)] [--c (int, bool, str] --d int{1905, 42}
baz.py: error: argument --d: invalid choice: 43 (choose from 42, 1905)
```

### Nested Types

Wrap your function in `Type` and then this can be passed as a higher-order type to annotations, then `aku` can recursively analysis them. For `Union` type, you can choose which type to run at command line interface. To avoid name conflicting, you can open a sub-namespace by adding a underline to your argument name.

```python
from typing import Type, Union
from aku import Aku


def add(x: int, y: int):
    print(f'{x} + {y} => {x + y}')


def sub(x: int, y: int):
    print(f'{x} - {y} => {x - y}')


aku = Aku()


@aku.option
def one(op: Union[Type[add], Type[sub]]):
    op()


@aku.option
def both(lhs_: Type[add], rhs_: Type[sub]):
    lhs_()
    rhs_()


if __name__ == '__main__':
    aku.run()
```

```shell script
~ python examples/qux.py one --op add --help 
usage: qux.py one [-h] [--op {add, sub}[fn]]

optional arguments:
  -h, --help           show this help message and exit
  --op {add, sub}[fn]  op (default: (<function add at 0x7fc1bc223700>, 'op'))
  --x int              x
  --y int              y

~ python examples/qux.py one --op add --x 1 --y 2
1 + 2 => 3

~ python examples/qux.py one --op sub --help     
usage: qux.py one [-h] [--op {add, sub}[fn]]

optional arguments:
  -h, --help           show this help message and exit
  --op {add, sub}[fn]  op (default: (<function sub at 0x7ff968a2db80>, 'op'))
  --x int              x
  --y int              y

~ python examples/qux.py one --op sub --x 1 --y 2
1 - 2 => -1

~ python examples/qux.py both --help             
usage: qux.py both [-h] --lhs-x int --lhs-y int --rhs-x int --rhs-y int

optional arguments:
  -h, --help   show this help message and exit
  --lhs-x int  lhs-x
  --lhs-y int  lhs-y
  --rhs-x int  rhs-x
  --rhs-y int  rhs-y

~ python examples/qux.py both --lhs-x 1 --lhs-y 2 --rhs-x 3 --rhs-y 4
1 + 2 => 3
3 - 4 => -1
```