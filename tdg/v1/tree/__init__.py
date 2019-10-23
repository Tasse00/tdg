from abc import ABC, abstractmethod
from typing import List, Optional, Dict


class ValueDesc:
    def __init__(self, field_name: str, complete_expr: str, protocol: Optional[str], expr: str):
        self.field_name = field_name
        self.complete_expr = complete_expr
        self.protocol = protocol
        self.expr = expr


class ObjNode:
    def __init__(self, model: str, alias: str, parent: 'ObjNode', values: Dict[str, ValueDesc]):
        self.model = model
        self.alias = alias
        self.parent = parent
        self.values = values

    def get_field_value_desc(self, field_name: str) -> ValueDesc:
        return self.values[field_name]


class BaseObjTreeParser(ABC):

    @abstractmethod
    def parse(self, data, parent: Optional[ObjNode]) -> List[ObjNode]:
        pass
