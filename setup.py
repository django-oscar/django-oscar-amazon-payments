#!/usr/bin/env python
from setuptools import setup, find_packages

from oscar_amazon_payments import VERSION


setup(
    name='django-oscar-amazon-payments',
    version=VERSION,
    url='https://github.com/tangentlabs/django-oscar-amazon-payments',
    author="Nathan Humphreys",
    author_email="nathan.humphreys@tangentsnowball.com",
    description=(
        "Integration with Amazon Payments for django-oscar"),
    long_description=open('README.rst').read(),
    keywords="Payment, amazon-payments, Oscar",
    license=open('LICENSE').read(),
    platforms=['linux'],
    packages=find_packages(exclude=['sandbox*', 'tests*']),
    include_package_data=True,
    install_requires=[
        'requests>=1.0',
        'django-localflavor'],
    extras_require={
        'oscar': ["django-oscar>=0.6"]
    },
    # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Other/Nonlisted Topic'],
)
