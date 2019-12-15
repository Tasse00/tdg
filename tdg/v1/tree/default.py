import uuid
from typing import Union, List, Optional

from marshmallow import Schema, fields, INCLUDE, ValidationError

from tdg.v1.tree import BaseObjTreeParser, ObjNode, ValueDesc


class DuplicateSchema(Schema):
    model = fields.String()
    alias = fields.String()
    items = fields.Nested("self", many=True, unknown=INCLUDE)
    duplicate = fields.Nested("self", many=True, unknown=INCLUDE)


class TreeSchema(Schema):
    model = fields.String(required=True)
    alias = fields.String()
    items = fields.Nested("self", many=True, unknown=INCLUDE)
    duplicate = fields.Nested(DuplicateSchema, many=True, unknown=INCLUDE)


class DefaultObjTreeParser(BaseObjTreeParser):
    """
    以'>'作为协议分隔符的DFS节点构造器
    """

    def __init__(self, proto_symbol: str = ">"):
        super(DefaultObjTreeParser, self).__init__()
        self.proto_symbol = proto_symbol

    def parse(self, node_desc: Union[dict, List[dict]], parent: Optional[ObjNode] = None):

        nodes: List[ObjNode] = []

        try:
            node_desc_list = [node_desc] if isinstance(node_desc, dict) else node_desc
            node_desc_json_list = TreeSchema(many=True, unknown=INCLUDE).load(node_desc_list)
        except ValidationError as e:
            raise RuntimeError("invalid data format for DefaultObjTreeParser\n" + str(e.messages))

        for node_desc in node_desc_json_list:

            dupl = node_desc.pop('duplicate', None)
            if dupl:
                shadow = node_desc.copy()

                for dupl_unit in dupl:
                    unit_shadow = shadow.copy()
                    unit_shadow.update(dupl_unit)
                    nodes.extend(self.parse(unit_shadow, parent))
                continue

            model = node_desc.pop('model', None)
            alias = node_desc.pop('alias', None) or "auto_alias-" + uuid.uuid4().__str__().replace("-", "")
            items = node_desc.pop('items', None)
            values = {}
            for k, v in node_desc.items():
                if not k.startswith('$'):
                    raise RuntimeError("obj tree desc error, value data not start with $, " + k)
                field_name = k[1:]
                coms = [com.strip() for com in v.split(self.proto_symbol, 1)]

                if len(coms) == 1:
                    values[field_name] = ValueDesc(field_name, v, None, coms[0])
                else:
                    protocol, expr = coms
                    values[field_name] = ValueDesc(field_name, v, protocol, expr)

            node = ObjNode(
                model=model,
                alias=alias,
                values=values,
                parent=parent
            )
            nodes.append(node)

            if items:
                nodes.extend(self.parse(items, node))

        return nodes
