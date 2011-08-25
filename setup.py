from setuptools import setup, find_packages
import sys, os

version = '1.1'

setup(name='TxScheduling',
      version=version,
      description="A scheduling plugin for Twisted",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "CONTRIBUTORS.rst")).read() + "\n\n" + 
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Twisted",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ],
      keywords='twisted python scheduling cron',
      author='Texas A&M University Library',
      author_email='webmaster@library.tamu.edu',
      maintainer='Benjamin Liles',
      maintainer_email='benliles@gmail.com',
      url='https://github.com/benliles/TxScheduling',
      packages=find_packages(),
      test_suite = 'txscheduling.tests.test_suite',
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Twisted>=8',
          'zope.interface',
      ])
