

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="toydb",
    version="0.0.1",
    author="Austin Poor",
    author_email="austinpoor@gmail.com",
    description="A small relational database writen in pure python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/a-poor/toydb",
    packages=setuptools.find_packages(),
     classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
