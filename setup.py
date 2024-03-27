from setuptools import setup, find_packages, Extension
import subprocess
import os, tempfile, shutil

VERSION="1.0.0"


def get_requirements():
    fname = f"{os.path.dirname(os.path.realpath(__file__))}/requirements.txt"
    with open(fname) as f:
        install_requires = f.read().splitlines()
    return install_requires


if __name__ == '__main__':

    setup(
        name='secretscientist',
        version=VERSION,
        description='secret scientist game',
        url='https://github.com/briling/secret-scientist',
        install_requires=get_requirements(),
        packages=setuptools.find_packages(exclude=['tests', 'examples']),
        include_package_data=True,
        package_data={'': ['data/*.*', 'people/*.*', 'scientists/*.*']},
    )
