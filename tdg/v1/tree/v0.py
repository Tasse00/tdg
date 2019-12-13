import logging
from dataclasses import dataclass
from typing import Optional, List

from tdg.v1.tree import BaseObjTreeParser, ObjNode


@dataclass
class Alias:
    alias: str


p = object()


def ref(alias):
    return Alias(alias)


class V0TreeParser(BaseObjTreeParser):
    """
    v0.x 版本的语法树

    关键词
    alias   |   可选  ｜   tdg选取所用别名
    model   |   必选  |   数据库模型
    items   |   可选  |   子对象定义列表，字对象的p关联指向当前对象
    insts   |   可选  |   副本列表，共用一批相同设置的obj定义副本
    ****    |   可选  |   传递给model实例化时的额外参数
    """

    def __init__(self,
                 model_field: str = "model",
                 alias_field: str = "alias",
                 items_field: str = "items",
                 insts_field: str = "insts",
                 *args, **kwargs):
        super(V0TreeParser, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger("tdg.parser.v0")
        self.model_field = model_field
        self.alias_field = alias_field
        self.items_field = items_field
        self.insts_field = insts_field

    def parse(self, cfg: dict, parent: Optional[ObjNode]) -> List[ObjNode]:
        not_meet_ref_nodes = []
        self.logger.debug('start gen data via config.')

        def worker(cfg, parent, indent):
            prefix = "  " * indent
            ori_cfg = cfg.copy()
            self.logger.debug("%s%s %s", prefix, 'parent', parent)
            self.logger.debug("%s%s %s", prefix, 'config', cfg)

            insts = cfg.pop(self.insts_field, None)
            if insts:
                for inst_cfg in insts:
                    this_cfg = cfg.copy()
                    this_cfg.update(inst_cfg)
                    self.logger.debug("%s%s %s", prefix, 'inst', this_cfg)
                    worker(this_cfg, parent=parent, indent=indent + 1)

            else:

                model = cfg.pop(self.model_field, None)
                alias = cfg.pop(self.alias_field, None)
                items = cfg.pop(self.items_field, None)
                self.logger.debug("%s%s %s", prefix, 'items', items)
                assert model

                ##
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
