import importlib
import inspect
import logging
import random
from typing import Dict, Any, List

import flask_sqlalchemy

from tds.rules import GeneralRule as GR, StringWithIncrSuffix, ConstGenerator, RandomChoice, Rule, \
    Generator
from tds.statement import Statement, AliasStatementOperation, AliasStatement
from tds.utils import parent_alias

logger = logging.getLogger('test.tds')


class AliasNotExisted(Exception):
    def __init__(self, alias):
        self.alias = alias


class TDS:

    def __init__(self, db: flask_sqlalchemy.SQLAlchemy, models_modules: List[str],
                 field_generator_config: Dict[Any, Dict[str, Rule]]):

        self._db = db

        # all models
        self._models = self._detect_all_models(db, models_modules)

        # {Model:{FIELD: GENERATOR}}
        self._gens = self._create_generators(field_generator_config)

        # [obj1, obj2, ...]
        self._objs = []

        # {alias:obj1, alias:obj2}
        self._alias = {}

    @classmethod
    def _create_generators(cls, config: Dict[Any, Dict[str, Rule]]) -> Dict[Any, Dict[str, Generator]]:
        """按照字段生成器规则实例化各生成器"""
        gens = {}
        for model, fields in config.items():
            if not model in gens:
                gens[model] = {}

            for fieldname, rule in fields.items():
                assert isinstance(rule, Rule)
                gens[model][fieldname] = rule.newGenerator()

        return gens

    @classmethod
    def _detect_all_models(cls, db: flask_sqlalchemy.SQLAlchemy, models_modules: List[str]) -> List:
        mods = []
        for module in models_modules:
            mod = importlib.import_module(module)
            for k in dir(mod):
                v = getattr(mod, k)
                try:
                    if issubclass(v, (db.Model,)):
                        mods.append(v)
                except:
                    # 兼容非class类型
                    pass
        return mods

    def __getitem__(self, item):
        return self._alias.get(item, None)

    def _clean_data(self):
        """清理数据表中所有数据"""
        ms = self._models.copy()

        while True:
            if not ms:
                break
            # this magic power!
            m = random.choice(ms)
            ms.remove(m)
            try:
                for o in m.query:
                    self._db.session.delete(o)
                self._db.session.commit()
            except Exception as e:
                self._db.session.rollback()
                ms.append(m)
        self._db.session.commit()

    def _setup(self):
        """建立数据库"""
        self._db.session().expire_on_commit = False  # 为了TDS['XX']始终可用
        self._clean_data()

    def _teardown(self):
        """删除数据库"""
        self._db.session().expire_on_commit = True
        self._clean_data()

    def _new_obj(self, _tds_Model, _tds_alias=None, _tds_commit=False, **kwargs):
        """
        新建某一Model的记录. alias作为该条记录别名.
        kw中的字段会自动映射到Model表的初始化. 若kw中存在_default值的字段,则会调用规则器生成新的一个值
        :raise InsufficientRule:
        """

        logger.debug("new '%s'<%s> with %s", _tds_alias, _tds_Model.__name__, kwargs)

        data = kwargs.copy()

        for field, gen in self._gens.get(_tds_Model, {}).items():
            if field not in kwargs:
                data[field] = gen.next()

        for k, v in kwargs.items():
            data[k] = v

        obj = _tds_Model(**data)
        self._db.session.add(obj)
        self._db.session.flush()
        if _tds_commit:
            self._db.session.commit()

        self._objs.append(obj)
        if _tds_alias:
            self._alias[_tds_alias] = obj

        return obj

    def _translate(self, data):
        # list 要检查element类型
        # dict 要检查dict items类型
        # callable 解析args，同名alias传入执行, 取结果
        # 其余检查是否为Statement类型

        if isinstance(data, dict):
            data = data.copy()
            for k, v in data.items():
                data[k] = self._translate(v)
            return data
        elif isinstance(data, (list, tuple)):
            data = data.copy()
            for idx, itm in enumerate(data):
                data[idx] = self._translate(itm)
            return data
        elif callable(data):
            sig = inspect.signature(data)
            args = []
            for alias, p in sig.parameters.items():

                # 在参数中，p代表父级变量
                # 存在对alias命名的局限性.
                # 是否需要约定callable类型字段无parent概念？
                if alias == 'p':
                    alias = parent_alias
                res = self[alias]
                if res is None:
                    logger.debug('alias %s not existed now.', alias)
                    raise AliasNotExisted(alias)

                args.append(res)
            return data(*args)

        elif isinstance(data, Statement):
            aso = AliasStatementOperation(data)
            obj = self[aso.alias]

            if obj is None:
                logger.debug('alias %s not existed now.', aso.alias)
                raise AliasNotExisted(aso.alias)
            return aso.exec(obj)
        else:
            return data

    def gen(self, cfg: dict, parent=None,
            model_field='model', alias_field='alias', items_field='items', insts_field='insts'):

        not_meet_ref_nodes = []
        logger.debug('start gen data via config.')

        def worker(cfg, parent, indent):
            prefix = "  " * indent
            ori_cfg = cfg.copy()
            logger.debug("%s%s %s", prefix, 'parent', parent)
            logger.debug("%s%s %s", prefix, 'config', cfg)

            insts = cfg.pop(insts_field, None)
            if insts:
                for inst_cfg in insts:
                    this_cfg = cfg.copy()
                    this_cfg.update(inst_cfg)
                    logger.debug("%s%s %s", prefix, 'inst', this_cfg)
                    worker(this_cfg, parent=parent, indent=indent + 1)

            else:

                model = cfg.pop(model_field, None)
                alias = cfg.pop(alias_field, None)
                items = cfg.pop(items_field, None)
                logger.debug("%s%s %s", prefix, 'items', items)
                assert model

                self._alias[parent_alias] = parent
                try:
                    cfg = self._translate(cfg)
                except AliasNotExisted as e:
                    not_meet_ref_nodes.append((ori_cfg, parent))
                    indent -= 1
                    return False

                obj = self._new_obj(model, alias, False, **cfg)

                if items:
                    for item_cfg in items:
                        worker(item_cfg.copy(), parent=obj, indent=indent + 1)

        worker(cfg, parent, 0)

        while True:
            if not not_meet_ref_nodes:
                break
            to_process_nodes = not_meet_ref_nodes.copy()
            not_meet_ref_nodes.clear()
            logger.debug("try gen unmeet ref levels")
            for n in to_process_nodes:
                worker(*n, indent=0)
            if len(to_process_nodes) == len(not_meet_ref_nodes):
                self._db.session.rollback()
                raise ValueError(
                    "existed circle reference or invalid ref in: %s" % ([n[0] for n in not_meet_ref_nodes]))

        self._db.session.commit()

        logger.debug('gen data via config finished.')
