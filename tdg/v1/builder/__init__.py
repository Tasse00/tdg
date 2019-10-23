import abc
from typing import List, Dict, Tuple

from flask_sqlalchemy import Model, SQLAlchemy

from tdg.v1.config import BaseModelConfigRepo
from tdg.v1.explainer import BaseExplainerRepo
from tdg.v1.tree import ObjNode


class BaseObjBuilder(abc.ABC):

    @abc.abstractmethod
    def build(self, db: SQLAlchemy,
              model_conf_repo: BaseModelConfigRepo,
              explainer_repo: BaseExplainerRepo,
              existed_objs: Dict[str, Model],
              nodes: List[ObjNode]) -> Tuple[Dict[str, Model], List[Model]]:
        """
        :param db:
        :param model_conf_repo: 模型配置仓库[modelName]
        :param explainer_repo:  字段解释器仓库
        :param existed_objs:    已存在的对象,alias为键
        :param nodes:           对象节点列表
        :return: (alias_objs, objs_list)
        """
        pass
