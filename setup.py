# -*- coding: utf-8 -*-

import os
from codecs import open
from setuptools import find_packages, setup

current_path = os.path.abspath(os.path.dirname(__file__))
os.chdir(os.path.abspath(current_path))

setup(
    name="aws-resource-monitor",
    version="1.0.0",
    description="Easily monitor CPU and memory usage in AWS Batch jobs and report them to StatsD",
    long_description=open("./README.md", "r").read(),
    long_description_content_type="text/markdown",
    author="Luigi's Box",
    author_email="support@luigisbox.com",
    url="https://www.luigisbox.com/",
    license="MIT",
    keywords="aws monitoring",
    packages=find_packages(),
    project_urls={
        "Bug Tracker": (
            "https://github.com/luigisbox/aws-resource-monitor/issues"
        ),
        "Source Code": "https://github.com/palosopko/aws-resource-monitor",
    },
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
)
