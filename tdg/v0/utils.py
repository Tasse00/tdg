import uuid
from typing import Optional


class Statement:
    def __init__(self, base: str, expr: Optional[str] = None):
        """

        :param base: 初始
        :param expr: 完整属性表达式, 默认与base相同
        """
        self._base = base
        self._expr = base if expr is None else expr

    def __getattribute__(self, item: str):
        if not item.startswith('_'):
            return self.__class__(self._base, self._expr + '.{}'.format(item))
        else:
            return super(Statement, self).__getattribute__(item)

    def __getitem__(self, item: str):
        return self.__class__(self._base, self._expr + '[{}]'.format(item))


parent_alias = 'parent_' + uuid.uuid4().__str__().replace('-', '')

p = Statement(parent_alias)
ref = Statement
