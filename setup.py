# coding:utf-8
# 引入构建包信息的模块
from distutils.core import setup
from setuptools import find_packages


# 依赖包
install_requires = [
    "pyecharts>=1.4.0"
]

# 定义发布的包文件的信息
setup(
    name="apm",            # 发布的包文件名称
    version="0.1.5",                     # 发布的包的版本序号
    description="安卓性能监控工具",      # 发布包的描述信息
    author="daiyang",                  # 发布包的作者信息
    author_email="daiyang@zuoyebang.com",  # 作者联系邮箱信息
    packages=find_packages(exclude=["info", "report", "venv", "README.md", "config.json"]),  # 去掉不打包的内容
    install_requires=install_requires,  # 依赖
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Programming Language :: Python :: 3.7'
    ],
    platforms="any",
    entry_points={                      # 命令行工具入口
            'console_scripts': [
                'apm=apm.cli:cli',
            ]
        }
)
