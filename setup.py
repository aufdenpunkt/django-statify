#!/usr/bin/env python
#

# Core imports
from setuptools import setup


INSTALL_REQUIRES = [
    'Django>=1.3',
    'requests>=1.1.0',
    'paramiko>=1.10.0',
    'scpclient>=0.4',
    'requests @ git+ssh://git@github.com/aufdenpunkt/django-medusa.git@v0.3.2',
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
    version='0.3.0',
    author='Christian Schweinhardt',
    author_email='are.u.kidding@me.com',
    license='BSD',
    url='https://github.com/aufdenpunkt/django-statify',
    download_url='https://github.com/aufdenpunkt/django-statify.git',
    package_dir={'statify': 'statify'},
    packages=['statify'],
    zip_safe=False,
    install_requires=INSTALL_REQUIRES,
    include_package_data=True,
    classifiers=CLASSIFIERS,
)
