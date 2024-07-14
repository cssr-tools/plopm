"""Simplified and flexible framework for plotting OPM Flow geological models"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf8") as file:
    long_description = file.read()

with open("requirements.txt", "r", encoding="utf8") as file:
    install_requires = file.read().splitlines()

with open("dev-requirements.txt", "r", encoding="utf8") as file:
    dev_requires = file.read().splitlines()

setup(
    name="plopm",
    version="2024.04",
    install_requires=install_requires,
    extras_require={"dev": dev_requires},
    setup_requires=["setuptools_scm"],
    description="Simplified and flexible framework for plotting OPM Flow geological models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cssr-tools/plopm",
    author="David Landa-Marbán",
    mantainer="David Landa-Marbán",
    mantainer_email="dmar@norceresearch.no",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    keywords="opm flow python plot mesh",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    license="GPL-3.0",
    python_requires=">=3.8, <4",
    entry_points={
        "console_scripts": [
            "plopm=plopm.core.plopm:main",
        ]
    },
    include_package_data=True,
)
