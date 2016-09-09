#!/usr/bin/env python
"""
aeexe

Author: Alpha <alpha@pokesplash.net>

"""

from setuptools import setup

setup(
    name='aeexe',
    version='0.1.0',
    description='aeexe',
    url='https://github.com/Alphadelta14/aeexe',
    author='Alphadelta14',
    author_email='alpha@pokesplash.net',
    license='MIT',
    install_requires=[
        'redis',
        'requests',
        'six'
    ],
    entry_points={
        'console_scripts': [
            'alterego=alterego.cli:main'
        ],
    },
    scripts=[
        'bin/alterego',
    ],
    packages=['alterego'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Artistic Software',
        'Topic :: Communications',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Puzzle Games',
        'Topic :: Games/Entertainment :: Role-Playing',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Text Processing :: Indexing',
        'Topic :: Text Processing :: Linguistic',
    ]
)
