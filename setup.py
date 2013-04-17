#!/usr/bin/env python
#

# Core imports
from setuptools import setup


dependency_links = [
    'https://github.com/christian-schweinhardt/django-medusa.git#egg=django_medusa'
]


install_requires = [
    'Django>=1.3',
    'requests>=1.1.0',
    'paramiko>=1.10.0',
    'scpclient>=0.4',
    'pycrypto>=2.6'
]


setup(
    name='django-statify',
    description='Build out a static version of your website and deploy it.',
    long_description='Build out a static version of your website and deploy it.',
    version='0.1.3',
    author='Christian Schweinhardt',
    author_email='are.u.kidding@me.com',
    license='BSD',
    url='https://github.com/christian-schweinhardt/django-statify',
    download_url='https://github.com/christian-schweinhardt/django-statify.git',
    package_dir={'statify': 'statify'},
    packages=['statify'],
    zip_safe=False,
    install_requires=install_requires,
    dependency_links = dependency_links,
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
