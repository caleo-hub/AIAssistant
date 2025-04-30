# setup.py
from setuptools import setup, find_packages

setup(
    name="rag_assistant",
    version="0.1.0",
    packages=find_packages(),  # vai detectar utils e quaisquer outros
    include_package_data=True,
)
