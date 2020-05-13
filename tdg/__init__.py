from copy import deepcopy
from typing import Type, List

from flask_sqlalchemy import Model

from tdg.v1.builder.default import DefaultObjBuilder
from tdg.v1.config import BaseModelConfigParser
from tdg.v1.config.default import DefaultModelConfigRepo, DefaultModelConfigParser
from tdg.v1.explainer.default import DefaultExplainerRepo
from tdg.v1.filler.default import DefaultFillerTypeRepo
from tdg.v1.tdg import BaseTdg
from tdg.v1.tree.default import DefaultObjTreeParser


class Tdg(BaseTdg):
    FillerTypeRepoCls = DefaultFillerTypeRepo
    ExplainerRepoCls = DefaultExplainerRepo
    ObjTreeParserCls = DefaultObjTreeParser
    ObjBuilderCls = DefaultObjBuilder
    ModelConfigParserCls = DefaultModelConfigParser
    ModelConfigRepoCls = DefaultModelConfigRepo

    def __init__(self,
                 db,
                 models: List[Type[Model]],
                 models_config: dict = None,
                 auto_clean_when_teardown: bool = True):
        """
        :param db: flask-sqlalchemy 实例 或者 session
        :param models: Model对象列表，用于自动清理
        :param models_config: 字段填充规则的配置
        :param auto_clean_when_teardown: 上下文使用时，自动清空数据库（不重建）
        """

        model_config_repo = self.ModelConfigRepoCls()
        model_config_parser = self.ModelConfigParserCls(model_config_repo, self.FillerTypeRepoCls())

        # 兼容传入的是迭代器对象
        models = deepcopy(list(models))

        self.parse_model_config(model_config_parser, models, models_config or {})

        super(Tdg, self).__init__(db,
                                  models,
                                  model_config_repo,
                                  self.ExplainerRepoCls(),
                                  self.ObjTreeParserCls(),
                                  self.ObjBuilderCls(),
                                  auto_clean_when_teardown)

    def parse_model_config(self, parser: BaseModelConfigParser, models: List[Type[Model]], models_config: dict):
        """解析model配置"""
        parser.parse_and_store(models, models_config)
