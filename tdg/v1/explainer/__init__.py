import abc
from typing import List, Union, Dict, Any, Type

from flask_sqlalchemy import Model


class BaseExplainer(abc.ABC):

    @abc.abstractmethod
    def get_supported_protocols(self) -> List[str]:
        """支持的Value Setter协议"""
        pass

    @abc.abstractmethod
    def need_objs(self, expr: str) -> List[Union[int, str]]:
        """需要的TDS实例alias"""
        pass

    @abc.abstractmethod
    def get_value(self, parents: List[Model], objs: Dict[Union[int, str], Model], expr: str) -> Any:
        """
        依据objs及expr获取值
        :param parents: 当前节点的父级向上直至根节点的obj列表 [Parent, .... , Root]
        :param objs: need_objs申请的实例
        """
        pass


class ExplainerExprError(Exception):
    def __init__(self, message):
        super(ExplainerExprError, self).__init__()
        self.message = message

    def __repr__(self):
        return f"<ValueExprError {self.message}>"


class BaseExplainerRepo(abc.ABC):

    @abc.abstractmethod
    def register(self, explainer_type: Type[BaseExplainer]):
        pass

    @abc.abstractmethod
    def get_explainer(self, explainer_proto: str) -> BaseExplainer:
        pass
