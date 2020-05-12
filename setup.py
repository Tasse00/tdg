from setuptools import setup, find_packages

setup(
    name='TDG',
    version="1.2.15",
    description=('基于flask-sqlalchemy的配置化测试数据生产工具'),
    long_description=open('README.md', encoding="utf8").read(),
    long_description_content_type='text/markdown',
    author='Aengine',
    author_email='zhangzheng@aengine.com.cn',
    maintainer='Carl.Zhang',
    maintainer_email='zhangzheng@aengine.com.cn',
    license='BSD License',
    packages=find_packages(include=("tdg*",)),
    install_requires=[
        'Flask_SQLAlchemy>=2.4,<=3.0',
        'marshmallow',
    ],
    platforms=["all"],
    url='https://gitlab.aengine.com.cn:aengine/tdg',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
)
