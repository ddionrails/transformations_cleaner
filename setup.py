""" Setup script for the transformations_cleaner package."""
from setuptools import find_packages, setup

setup(
    name="transformations_cleaner",
    version="0.0.1",
    url="https://github.com/ddionrails/transformations_cleaner",
    description="Clean relations from a generations file",
    long_description=open("./README.md").read(),
    author="Dominque Hansen",
    author_email="dhansen@diw.de",
    python_requires=">=3.6.0",
    packages=find_packages(),
    install_requires=["pandas >= 0.25.0", "networkx >= 2.4"],
    entry_points={
        "console_scripts": [
            "clean_transformations = transformations_cleaner.__main__:main"
        ]
    },
    license="BSD 3-Clause",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: BSD License",
    ],
    keywords=["paneldata", "humanities"],
)
