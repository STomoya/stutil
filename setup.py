
from setuptools import find_packages, setup

import stutil

setup(
    name='stutil',
    version=stutil.__version__,
    license='MIT',
    description='UTILities for STomoya.',
    author='Tomoya Sawada (STomoya)',
    author_email='stomoya0110@gmail.com',
    url='https://github.com/STomoya/stutil/',
    packages=find_packages(),
    install_requires=[
        'pyyaml',
    ]
)
