from typing import Type, List

from flask_sqlalchemy import Model, SQLAlchemy

from tdg.v1.builder.default import DefaultObjBuilder
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
                 db: SQLAlchemy,
                 models: List[Type[Model]],
                 models_config: dict,
                 auto_clean_when_teardown: bool = True):
        """
        :param db: flask-sqlalchemy 实例
        :param models: Model对象列表，用于自动清理
        :param models_config: 字段填充规则的配置
        :param auto_clean_when_teardown: 上下文使用时，自动清空数据库（不重建）
        """

        model_config_repo = self.ModelConfigRepoCls()
        model_config_parser = self.ModelConfigParserCls(model_config_repo, self.FillerTypeRepoCls())
        model_config_parser.parse_and_store(models, models_config)

        super(Tdg, self).__init__(db,
                                  models,
                                  model_config_repo,
                                  self.ExplainerRepoCls(),
                                  self.ObjTreeParserCls(),
                                  self.ObjBuilderCls(),
                                  auto_clean_when_teardown)
