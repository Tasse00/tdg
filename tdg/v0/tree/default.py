import inspect
import logging
import types
import uuid
from dataclasses import dataclass
from typing import Optional, List, Union

from tdg.v0.utils import Statement, parent_alias
from tdg.v1.tree import BaseObjTreeParser, ObjNode, ValueDesc


@dataclass
class Alias:
    alias: str


p = object()


def ref(alias):
    return Alias(alias)


class DefaultObjTreeParser(BaseObjTreeParser):
    """
    v0.x 版本的语法树

    ### 字段说明

    | field    | must | desc                                                         |
    | -------- | ---- | ------------------------------------------------------------ |
    | model    | √    | 声明该条记录的类型．                                         |
    | alias    | ×    | 指定该条记录的访问别名．                                     |
    | items    | ×    | 该条记录在逻辑上的子项．                                     |
    | insts    | ×    | 用于批量制定字项，存在该字段时会将当前其他字段作为inst中各记录实例的默认值. |
    | ****     | ×    | 传递给Model实例化方法                                        |

    ### 特殊值及特殊方法

    | 字段值     | 描述                                                     |
    | ---------- | -------------------------------------------------------- |
    | 可调用方法 | 会将与方法的参数名相同alias的obj传入. 返回值作为该字段值 |
    | p          | 代表父级object对象                                       |
    | ref()      | 相当于　lambda v: v, 操作方式与p相同
    """

    def __init__(self,
                 model_field: str = "model",
                 alias_field: str = "alias",
                 items_field: str = "items",
                 insts_field: str = "insts",
                 *args, **kwargs):
        super(DefaultObjTreeParser, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger("tdg.parser.v0")
        self.model_field = model_field
        self.alias_field = alias_field
        self.items_field = items_field
        self.insts_field = insts_field

    def parse(self, node_desc_list: Union[dict, List[dict]], parent: Optional[ObjNode] = None) -> List[ObjNode]:

        nodes: List[ObjNode] = []

        self.logger.debug('start gen data via config.')

        if isinstance(node_desc_list, dict):
            node_desc_list = [node_desc_list]

        for node_desc in node_desc_list:
            insts = node_desc.pop(self.insts_field, [])

            # 按照副本逻辑进行处理
            if insts:
                shadow = node_desc.copy()
                for inst_desc in insts:
                    inst_unit = shadow.copy()
                    inst_unit.update(inst_desc)
                    nodes.extend(self.parse(inst_unit, parent))
                continue

            model = node_desc.pop(self.model_field, None).__name__
            alias = node_desc.pop(self.alias_field, None) or "auto_alias_" + uuid.uuid4().__str__().replace("-", "")
            items = node_desc.pop(self.items_field, None)

            values = {}
            for k, v in node_desc.items():

                field_name = k

                if isinstance(v, types.LambdaType):
                    # lambda 表达式
                    # values[field_name] = ValueDesc(field_name, v, None, v)
                    line = inspect.getsource(v).strip()
                    startIdx = line.find('lambda')
                    val = line[startIdx:]
                    # 源码中一行最后存在','导致加载出来后是个元组
                    if val[-1] == ',':
                        val = val[:-1]
                    complete = 'calc>' + val
                    values[field_name] = ValueDesc(field_name, complete, 'calc', val)

                elif isinstance(v, Statement):
                    # Statement表达式
                    if v._base == parent_alias:
                        expr = 'lambda {}: {}'.format(parent.alias, v._expr.replace(parent_alias, parent.alias))
                        complete = 'calc>' + expr
                        values[field_name] = ValueDesc(field_name, complete, 'calc', expr)
                    else:
                        expr = 'lambda {}: {}'.format(v._base, v._expr)
                        complete = 'calc>' + expr
                        values[field_name] = ValueDesc(field_name, complete, 'calc', expr)
                elif isinstance(v, (list, tuple)):

                    # 兼容 [ref('a'), p.id] 此类情景
                    if all([isinstance(item, Statement) for item in v]):

                        alias_list = []
                        value_list = []
                        for sm in v:
                            if sm._base == parent_alias:
                                alias_list.append(parent.alias)
                                value_list.append(sm._expr.replace(parent_alias, parent.alias))
                            else:
                                alias_list.append(sm._base)
                                value_list.append(sm._expr)

                        expr = 'lambda {}: [{}]'.format(", ".join(alias_list), ", ".join(value_list))
                        complete = 'calc>' + expr
                        values[field_name] = ValueDesc(field_name, complete, 'calc', expr)

                    else:
                        values[field_name] = ValueDesc(field_name, v, None, v)

                else:
                    values[field_name] = ValueDesc(field_name, v, None, v)

            node_desc = ObjNode(
                model=model,
                alias=alias,
                values=values,
                parent=parent
            )
            nodes.append(node_desc)

            if items:
                nodes.extend(self.parse(items, node_desc))

        return nodes
