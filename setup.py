from setuptools import setup

setup(
    name='TDG',
    version="0.1.0",
    description=('基于flask-sqlalchemy的配置化测试数据生产工具'),
    long_description=open('README.md').read(),
    author='Aengine',
    author_email='zhangzheng@aengine.com.cn',
    maintainer='Carl.Zhang',
    maintainer_email='zhangzheng@aengine.com.cn',
    license='BSD License',
    packages=['tdg'],
    install_requires=[
        'Flask-SQLAlchemy',
    ],
    platforms=["all"],
    url='https://gitee.com/zhangbingxue/TDS',
)
