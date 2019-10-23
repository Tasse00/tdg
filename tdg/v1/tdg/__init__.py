import random
from typing import Union, List

import flask_sqlalchemy

from tdg.v1.builder import BaseObjBuilder
from tdg.v1.config import BaseModelConfigRepo
from tdg.v1.explainer import BaseExplainerRepo
from tdg.v1.tree import BaseObjTreeParser


class BaseTdg:

    def __init__(self, db: flask_sqlalchemy.SQLAlchemy,
                 model_conf_repo: BaseModelConfigRepo,
                 explainer_repo: BaseExplainerRepo,
                 obj_tree_parser: BaseObjTreeParser,
                 obj_builder: BaseObjBuilder):
        self.db = db
        self.model_conf_repo = model_conf_repo
        self.explainer_repo = explainer_repo
        self.obj_tree_parser = obj_tree_parser
        self.obj_builder = obj_builder

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

    def _clean_objs(self):
        """清除当前tdg实例生成的数据"""
        max_retries = 400  # 放置依赖项无法删除
        retries = 0
        objs = self.objs
        while objs:
            obj = random.choice(objs)
            objs.remove(obj)
            # TODO 是否可以全部remove后再commit?
            try:
                self.db.session.delete(obj)
                self.db.session.commit()
            except Exception as e:
                retries += 1
                self.db.session.rollback()
                objs.append(obj)
            else:
                retries = 0
            if retries >= max_retries:
                raise RuntimeError("clean obj reached max retries limit! " + str(self.alias_objs))

    def setup(self):
        self.db.session().expire_on_commit = False

    def teardown(self):
        self._clean_objs()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()

    def __enter__(self):
        self.setup()
        return self

    def __getitem__(self, item):
        return self.alias_objs[item]
