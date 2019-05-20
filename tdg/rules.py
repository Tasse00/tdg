import random


class Generator:
    def next(self):
        pass


class Rule:
    def newGenerator(self) -> Generator:
        return Generator()


class GeneralRule(Rule):
    def __init__(self, gencls, *args, **kwargs):
        self.gencls = gencls
        self.args = args
        self.kwargs = kwargs

    def newGenerator(self) -> Generator:
        return self.gencls(*self.args, **self.kwargs)


class ConstGenerator(Generator):
    """常量生成器"""

    def __init__(self, v):
        self.v = v

    def next(self):
        return self.v


class StringWithIncrSuffix(Generator):
    """带有自增后缀的字符串"""

    def __init__(self, basestr: str = "", start: int = 0):
        super(StringWithIncrSuffix, self).__init__()
        self.basestr = basestr
        self.idx = start

    def next(self) -> str:
        self.idx += 1
        return "%s%d" % (self.basestr, self.idx - 1)


class IncrInteger(Generator):
    """自增整型"""

    def __init__(self, base: int = 0):
        super(IncrInteger, self).__init__()
        self.num = base

    def next(self) -> int:
        self.num += 1
        return self.num - 1


class RandomChoice(Generator):
    """随机选项"""

    def __init__(self, choices: list):
        self.choices = choices

    def next(self):
        return random.choice(self.choices)
