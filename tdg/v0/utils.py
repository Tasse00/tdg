import uuid


class Statement:
    def __init__(self, base: str):
        self._base = base
        self._expr = base

    def __getattribute__(self, item: str):
        if not item.startswith('_'):
            self._expr += '.{}'.format(item)
            return self
        else:
            return super(Statement, self).__getattribute__(item)

    def __getitem__(self, item: str):
        self._expr += '[{}]'.format(item)
        return self


parent_alias = 'parent_' + uuid.uuid4().__str__().replace('-', '')

p = Statement(parent_alias)
ref = Statement
