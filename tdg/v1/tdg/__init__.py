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

    def _clean_many_to_many_records(self, model):
        """删除多对多字段所使用的关系表记录"""

        m2m_fields = []  # many to many fields
        for attr in dir(model):
            val = getattr(model, attr)
            if isinstance(val, InstrumentedAttribute):
                if isinstance(val.expression, BooleanClauseList):
                    m2m_fields.append(attr)  # 多对多字段

        if m2m_fields:

            for obj in model.query.all():
                # 健壮性处理:
                # 假如存在两个多对多的Model: Blog, Tag
                # 在业务代码中，如果出现　blog_obj.tags += [tag_obj] 形式代码，就有可能造成 blog_obj.tags 中存在重复tag对象的问题
                # 但是数据库中的中间表并不会插入多条关联记录 (sqlalchemy保证)，即sqlalchemy model的缓存并未同步数据库
                # 处理方式：若set后长度不同，则刷新该对象
                for field in m2m_fields:
                    rel_values = getattr(obj, field, [])
                    if len(set(rel_values)) != len(rel_values):
                        self.db.session.refresh(obj)
                        break

                for field in m2m_fields:
                    setattr(obj, field, [])

            self.db.session.flush()

    def clean_db(self):
        """清除数据库全部数据"""
        max_retries = 400  # 放置依赖项无法删除陷入死循环
        retries = 0
        rest_models = self.total_models.copy()
        while rest_models:
            model = random.choice(rest_models)

            self._clean_many_to_many_records(model)

            try:
                model.query.delete()
                self.db.session.flush()
                rest_models.remove(model)
                retries = 0
            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    raise RuntimeError("clean obj reached max retries limit! " + str(e))

        self.db.session.commit()

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
