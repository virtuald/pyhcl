#!/usr/bin/env python

from os.path import dirname, join
from distutils.core import setup

try:
    from setuptools.command.install import install as _install
except ImportError:
    from distutils.command.install import install as _install

import sys

setup_dir = dirname(__file__)

def _post_install():
    '''Initialize the parse table at install time'''
    import hcl
    from hcl.parser import HclParser
    parser = HclParser()


class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, (), msg="Generating parse table...")


def get_version():
    d = {}
    with open(join(setup_dir, 'src', 'hcl', 'version.py')) as fp:
        exec(compile(fp.read(), 'version.py', 'exec'), {}, d)
    return d['__version__'] 

install_requires=open(join(setup_dir, 'requirements.txt')).readlines()

setup(name='pyhcl',
      version=get_version(),
      description='HCL configuration parser for python',
      author='Dustin Spicuzza',
      author_email='dustin@virtualroadside.com',
      package_dir={'': 'src'},
      packages=['hcl'],
      scripts=["scripts/hcltool"],
      install_requires=install_requires,
      cmdclass={'install': install})


