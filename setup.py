#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
 
setup(
    name='django-database-files',
    version='0.2',
    description='A storage system for Django that stores uploaded files in the database. Based on Ben Fisherman\'s module and django snippet 1095',
    author='Ben Fisherman, Jens Alm',
    author_email='ben@firshman.co.uk, jens.alm@mac.com',
    url='http://github.com/ulmus/django-database-files/',
    packages=[
        'database_files',
    ],
    classifiers=['Development Status :: 4 - Beta',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 ],
)
