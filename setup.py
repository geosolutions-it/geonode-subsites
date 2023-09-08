from setuptools import find_packages, setup

import subsites


def read_file(path: str):
    with open(path, "r") as file:
        return file.read()


setup_requires = [
    "wheel",
]

setup(
    name="geonode-subsites",
    version=subsites.__version__,
    url=subsites.__url__,
    description=subsites.__doc__,
    long_description="A GeoNode 4.x app that implements subsites",
    author=subsites.__author__,
    author_email=subsites.__email__,
    platforms="any",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django :: 3.20",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(),
    package_data={"subsites": ["templates/*.html"]},
    include_package_data=True,
    install_requires=[
    ],
)
