import random
import string
from datetime import datetime
from typing import Dict, Type

from tdg.v1.filler import BaseFillerTypeRepo, BaseFiller


class DefaultFillerTypeRepo(BaseFillerTypeRepo):

    def __init__(self):
        self.filler_types: Dict[str, Type[BaseFiller]] = {}
        self._register_default_fillers()

    def _register_default_fillers(self):
        for filler_type in default_filler_types:
            self.register(filler_type)

    def register(self, filler: Type[BaseFiller]):
        self.filler_types[filler.__name__] = filler

    def create_filler(self, filler_type_name: str, args, kwargs) -> BaseFiller:
        return self.filler_types[filler_type_name](*args, **kwargs)


class RandomString(BaseFiller):

    def __init__(self, prefix="", suffix="", length=4, candidate=string.ascii_letters):
        super(RandomString, self).__init__()
        self.prefix = prefix
        self.suffix = suffix
        self.length = length
        self.candidate = candidate

    def generate(self):
        return self.prefix + "".join(random.choice(self.candidate) for _ in range(self.length)) + self.suffix


class RandomNumber(BaseFiller):

    def __init__(self, min=0, max=10, round=False):
        super(RandomNumber, self).__init__()
        self.min = min
        self.max = max
        self.round = round

    def generate(self):
        val = random.random() * (self.max - self.min) + self.min
        if self.round:
            val = round(val)
        return val


class IncrNumber(BaseFiller):

    def __init__(self, base=1, step=1):
        super(IncrNumber, self).__init__()
        self.base = base
        self.step = step

    def generate(self):
        return self.base + (self.index - 1) * self.step


class DateTime(BaseFiller):

    def __init__(self, fixed_date=None, fixed_format="YYYY-mm-dd HH:MM:SS"):
        super(DateTime, self).__init__()
        self.fixed_date = fixed_date
        self.fixed_format = fixed_format
        if self.fixed_date:
            self.fixed_value = datetime.strptime(self.fixed_date, self.fixed_format)

    def generate(self):
        if self.fixed_date:
            return self.fixed_value
        else:
            return datetime.now()


default_filler_types = [
    RandomString,
    RandomString,
    IncrNumber,
    DateTime,
]
