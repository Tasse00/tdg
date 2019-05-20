import enum
from typing import Any, List


class ActionType(enum.Enum):
    Attrib = 'attrib'
    Item = 'item'  # [0] ['key']


class Action:
    def __init__(self, type: ActionType, v: Any):
        self.type = type
        self.v = v

    def process(self, tgt):
        if self.type == ActionType.Attrib:
            # print('get attrib %s from %s' % (self.v, tgt))
            return getattr(tgt, self.v)
        elif self.type == ActionType.Item:
            # print('get item %s from %s' % (self.v, tgt))
            return tgt[self.v]
        else:
            raise ValueError('invalid action type: %s' % self.v)

    def __str__(self):
        if self.type is ActionType.Attrib:
            return ".%s" % self.v
        elif self.type is ActionType.Item:
            return "[%s]" % self.v.__repr__()
        else:
            raise ValueError('invalid action type: %s' % self.v)

    def __repr__(self):
        return "<Action %s>" % self


class Attrib:
    def __init__(self, v):
        self.v = v

    def get_from(self, obj):
        return obj[self]


class Statement:
    """预定义表达式，可接受任意attrib及item访问"""

    def __init__(self, prev=None, action=None):
        self.prev = prev
        self.action = action

    def __getattribute__(self, item):
        return Statement(prev=self, action=Action(ActionType.Attrib, item))

    def __getitem__(self, item):
        if isinstance(item, Attrib):
            return super(Statement, self).__getattribute__(item.v)
        else:
            return Statement(prev=self, action=Action(ActionType.Item, item))


class StatementOperation:

    def __init__(self, st: Statement):
        self._st = st

    def attr(self, item):
        return self._st[Attrib(item)]

    def exec(self, target: Any) -> Any:
        tmp = target
        for act in self.list_actions():
            tmp = act.process(tmp)

        return tmp

    def list_statements(self) -> List[Statement]:
        st_list = []

        s = self._st
        while True:
            if s is None:
                break
            st_list.append(s)
            so = self.__class__(s)
            s = so.attr('prev')

        st_list.reverse()
        return st_list

    def list_actions(self) -> List[Action]:
        return [StatementOperation(st).attr('action') for st in self.list_statements() if
                StatementOperation(st).attr('action')]

    def get_expr(self, prefix: str = '') -> str:
        return prefix + ''.join(str(act) for act in self.list_actions())


class AliasStatement(Statement):
    def __init__(self, alias: str):
        self.alias = alias
        super(AliasStatement, self).__init__()

    def __str__(self):
        return "<AliasStatement %s>" % self.alias

    def __repr__(self):
        return str(self)


class AliasStatementOperation(StatementOperation):

    @property
    def alias(self) -> str:
        return self.__class__(self.list_statements()[0]).attr('alias')
