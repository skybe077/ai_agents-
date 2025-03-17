# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 11:32:15 2025

@author: user
"""

from setuptools import setup, find_packages

setup(
    name="my_utils",                 # Package name for the combined package
    version="1.0.0",
    packages=find_packages(),         # Automatically finds db_utils and text_utils
    install_requires=[],              # Add dependencies here if needed
    description="A collection of utility packages for databases and text processing",
    author="ET",
    author_email="skybe077@ymail.com",
    url="https://github.com/your_repo/my_utils",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)