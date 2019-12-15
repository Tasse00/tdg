from typing import Type, List

from flask_sqlalchemy import Model, SQLAlchemy

from tdg.v1.builder.default import DefaultObjBuilder
from tdg.v1.config.default import DefaultModelConfigRepo, DefaultModelConfigParser
from tdg.v1.explainer.default import DefaultExplainerRepo
from tdg.v1.filler.default import DefaultFillerTypeRepo
from tdg.v1.tdg import BaseTdg
from tdg.v1.tree.default import DefaultObjTreeParser


class Tdg(BaseTdg):
    default_filler_type_repo = DefaultFillerTypeRepo()
    default_explainer_repo = DefaultExplainerRepo()
    default_obj_tree_parser = DefaultObjTreeParser()
    default_obj_builder = DefaultObjBuilder()

    def __init__(self, db: SQLAlchemy, models: List[Type[Model]], models_config: dict):
        """
        :param db: flask-sqlalchemy 实例
        :param models: Model对象列表，用于自动清理
        :param models_config_desc: 字段填充规则的配置
        """
        model_config_repo = DefaultModelConfigRepo()
        model_config_parser = DefaultModelConfigParser(model_config_repo, self.default_filler_type_repo)
        model_config_parser.parse_and_store(models, models_config)

        super(Tdg, self).__init__(db,
                                  model_config_repo,
                                  self.default_explainer_repo,
                                  self.default_obj_tree_parser,
                                  self.default_obj_builder)
