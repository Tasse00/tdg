import random
from typing import Union, List, Type

import flask_sqlalchemy
from flask_sqlalchemy import Model
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import BooleanClauseList

from tdg.v1.builder import BaseObjBuilder
from tdg.v1.config import BaseModelConfigRepo
from tdg.v1.explainer import BaseExplainerRepo
from tdg.v1.tree import BaseObjTreeParser


class BaseTdg:

    def __init__(self, db: flask_sqlalchemy.SQLAlchemy,
                 models: List[Type[Model]],
                 model_conf_repo: BaseModelConfigRepo,
                 explainer_repo: BaseExplainerRepo,
                 obj_tree_parser: BaseObjTreeParser,
                 obj_builder: BaseObjBuilder,
                 auto_clean_when_teardown: bool):
        """
        :param auto_clean_when_teardown: 上下文使用时，自动清空数据库（不重建）
        """
        self.db = db
        self.total_models = models
        self.model_conf_repo = model_conf_repo
        self.explainer_repo = explainer_repo
        self.obj_tree_parser = obj_tree_parser
        self.obj_builder = obj_builder
        self.auto_clean_when_teardown = auto_clean_when_teardown

        self.alias_objs = {}
        self.objs = []

    def gen(self, tree_desc: Union[List[dict], dict]) -> 'BaseTdg':
        nodes = self.obj_tree_parser.parse(tree_desc, None)

        alias_objs, objs = self.obj_builder.build(
            self.db,
            self.model_conf_repo,
            self.explainer_repo,
            self.alias_objs,
            nodes
        )
        self.alias_objs.update(alias_objs)
        self.objs.extend(objs)
        return self

    def clean_db(self):
        """清除数据库全部数据"""
        max_retries = 400  # 放置依赖项无法删除陷入死循环
        retries = 0
        rest_models = self.total_models.copy()
        while rest_models:
            model = random.choice(rest_models)

            ## 删除多对多的Table
            # 获取多对多的字段
            fields = []
            for attr in dir(model):
                val = getattr(model, attr)
                if isinstance(val, InstrumentedAttribute):
                    if isinstance(val.expression, BooleanClauseList):
                        fields.append(attr)  # 多对多字段
            if fields:
                for obj in model.query.all():
                    for field in fields:
                        setattr(obj, field, [])
                    self.db.session.add(obj)
                    self.db.session.flush()

            try:
                model.query.delete()
                self.db.session.commit()
                rest_models.remove(model)
                retries = 0
            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    raise RuntimeError("clean obj reached max retries limit! " + str(e))

    def setup(self):
        self.db.session().expire_on_commit = False

    def teardown(self):
        if self.auto_clean_when_teardown:
            self.clean_db()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()

    def __enter__(self):
        self.setup()
        return self

    def __getitem__(self, item):
        return self.alias_objs[item]
