#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
集装箱装载管理系统安装配置
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="container-loader",
    version="1.0.0",
    author="集装箱装载管理系统开发团队",
    author_email="contact@example.com",
    description="集装箱装载管理系统 - 优化集装箱装载过程的专业工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/container-loader",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Manufacturing",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "container-loader=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
        "data": ["*"],
        "resources": ["*"],
    },
)