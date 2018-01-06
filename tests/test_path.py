import argumentize
from argumentize.annotations import Path

app = argumentize.App()


@app.register
def expanduser(p: Path(expanduser=True) = '.'):
    print(p)


@app.register
def absolute(p: Path(absolute=True) = '.'):
    print(p)


@app.register
def mkdir(p: Path(ensure=True, mkdir=True) = 'out'):
    print(p)


@app.register
def ensure(p: Path(ensure=True) = 'out'):
    print(p)
    # TODO why this not work


app.run()