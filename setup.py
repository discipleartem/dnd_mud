"""Setup для D&D MUD."""

from setuptools import setup, find_packages

setup(
    name="dnd_mud",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "pyyaml>=6.0",
    ],
)