from setuptools import setup
from setuptools.command.install import install
import sys, os, stat
from shutil import copyfile

__PROG_NAME__ = 'zdeploy'
__VERSION__ = '1.1.0'

setup(
        name=__PROG_NAME__,
        version=__VERSION__,
        license=open('LICENSE').read(),
        url='https://github.com/ziggurattech/%s' % __PROG_NAME__,
        author='Fadi Hanna Al-Kass',
        author_email='f_alkass@zgps.live',
        description='General-purpose host deployment utility',
        long_description=open('README.md').read(),
        keywords='deployment automation framework',
        packages=[__PROG_NAME__],
        install_requires=open('requirements.txt').read().split('\n'),
        entry_points={
            'console_scripts': ['{prog} = {prog}:main'.format(prog=__PROG_NAME__)],
        }
)
