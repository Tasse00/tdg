import abc
from typing import Type


class BaseFiller(abc.ABC):

    def __init__(self, *args, **kwargs):
        self.index = 0

    @abc.abstractmethod
    def generate(self):
        """生成下一个值"""
        pass

    def next(self):
        val = self.generate()
        self.index += 1
        return val


class BaseFillerTypeRepo(abc.ABC):

    @abc.abstractmethod
    def register(self, filler: Type[BaseFiller]):
        pass

    @abc.abstractmethod
    def create_filler(self, filler_type_name: str, arg, kwargs) -> BaseFiller:
        pass
