#!/usr/bin/env python3
import os
from setuptools import setup, find_packages

with open('README.md', 'r') as r:
    README = r.read()

setup(
    name='flask-simple-captcha',
    version='1.1.0',
    description='Extremely simple, "Good Enough" captcha implemention for flask forms. No server side sessions required.',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/cc-d/flask-simple-captcha',
    author='Cary Carter',
    author_email='ccarterdev@gmail.com',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7'
    ],
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    install_requires=['Werkzeug==0.16.0', 'Pillow==8.3.1']
)
