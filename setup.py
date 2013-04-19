#!/usr/bin/env python
#

# Core imports
from setuptools import setup


DEPENDENCY_LINKS = [
    'https://github.com/christian-schweinhardt/django-medusa.git#egg=django_medusa'
]


INSTALL_REQUIRES = [
    'Django>=1.3',
    'requests>=1.1.0',
    'paramiko>=1.10.0',
    'scpclient>=0.4'
]


CLASSIFIERS = [
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Operating System :: OS Independent',
    'Topic :: Software Development',
    'Framework :: Django',
    'License :: OSI Approved :: BSD License',
    'Environment :: Web Environment'
]


setup(
    name='django-statify',
    description='Build out a static version of your website.',
    long_description='Build out a static version of your django project and deploy it using ftp, ssh or on your localhost.',
    version='0.1.6',
    author='Christian Schweinhardt',
    author_email='are.u.kidding@me.com',
    license='BSD',
    url='https://github.com/christian-schweinhardt/django-statify',
    download_url='https://github.com/christian-schweinhardt/django-statify.git',
    package_dir={'statify': 'statify'},
    packages=['statify'],
    zip_safe=False,
    install_requires=INSTALL_REQUIRES,
    dependency_links = DEPENDENCY_LINKS,
    include_package_data=True,
    classifiers=CLASSIFIERS,
)
