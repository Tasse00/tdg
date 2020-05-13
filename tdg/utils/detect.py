import importlib
import pkgutil
from typing import Union, List


def detect_models(base, dirs: Union[List[str], str]):
    """
    探测所有的Models
    :param base: 用于判断Model的基类，`issubclass(cls, base)?`
    :param dirs: model文件所在的目录
    """

    if not isinstance(dirs, (list, tuple)):
        dirs = [dirs]

    for file_finder, name, is_package in pkgutil.iter_modules(dirs):
        ## 不可以使用以下方式，下述方式每次都会新创建module，
        ## 使得sqlalchemy model的基类Base每次都是不同的值
        # loader = file_finder.find_module(name)
        # mod = loader.load_module()

        mod = importlib.import_module(
            file_finder.path.replace('/', '.') + '.' + name
        )

        for attr in dir(mod):
            if attr.startswith("_"):
                continue
            val = getattr(mod, attr)

            if isinstance(val, type) and issubclass(val, base) and val is not base:
                yield val
