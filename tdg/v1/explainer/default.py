import inspect
from typing import Type, Dict, List, Union, Any

from flask_sqlalchemy import Model

from tdg.utils import dotval
from tdg.v1.explainer import BaseExplainerRepo, BaseExplainer


class DefaultExplainerRepo(BaseExplainerRepo):

    def __init__(self):
        self.explainer_store: Dict[str, BaseExplainer] = {}
        self._register_default_explainers()

    def register(self, explainer_type: Type[BaseExplainer]):
        explainer = explainer_type()

        for proto in explainer.get_supported_protocols():
            self.explainer_store[proto] = explainer

    def get_explainer(self, explainer_proto: str) -> BaseExplainer:
        return self.explainer_store[explainer_proto]

    def _register_default_explainers(self):
        for explainer_type in default_explainer_types:
            self.register(explainer_type)


class AliasFieldSetter(BaseExplainer):
    """通过alias获取已存在的obj,并对其做点操作"""

    def get_supported_protocols(self) -> List[str]:
        return ["ref"]

    def need_objs(self, expr: str) -> List[Union[int, str]]:
        return [expr.strip().split('.')[0]]

    def get_value(self, parents: List[Model], objs: Dict[Union[int, str], Model], expr: str) -> Any:
        obj_key, dot_expr = expr.strip().split('.', 1)
        return dotval.get(objs[obj_key], dot_expr)


class ParentFieldSetter(BaseExplainer):
    """依赖父级做点操作"""

    def get_supported_protocols(self) -> List[str]:
        return ["p", "parent"]

    def need_objs(self, expr: str) -> List[Union[int, str]]:
        return []

    def get_value(self, parents: List[Model], objs: Dict[Union[int, str], Model], expr: str) -> Any:

        coms = expr.strip().split('.', 1)
        if len(coms) == 2:
            _, dot_expr = coms
            return dotval.get(parents[0], dot_expr)
        else:
            return parents[0]


class LambdaFieldSetter(BaseExplainer):
    """采用lambda做自定义操作,lambda的形参列表将会按同名获取tdg中的Obj"""

    def get_supported_protocols(self) -> List[str]:
        return ["calc"]

    def need_objs(self, expr: str) -> List[Union[int, str]]:
        lmd = eval(expr)
        sig = inspect.signature(lmd)
        return list(sig.parameters.keys())

    def get_value(self, parents: List[Model], objs: Dict[Union[int, str], Model], expr: str) -> Any:
        lmd = eval(expr)
        sig = inspect.signature(lmd)
        args = [objs[param] for param in sig.parameters.keys()]
        return lmd(*args)


default_explainer_types = [
    AliasFieldSetter,
    ParentFieldSetter,
    LambdaFieldSetter,
]
