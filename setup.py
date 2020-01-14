from setuptools import setup
from setuptools.command.install import install
import sys, os, stat
from shutil import copyfile

__PROG_NAME__ = 'zdeploy'

class Installer(install):
    def run(self):
        print('Installing %s' % __PROG_NAME__)
        platform = sys.platform.lower()
        if 'linux' in platform:
                dest = '/usr/bin/%s' % __PROG_NAME__
                copyfile(__PROG_NAME__, dest)
                os.chmod(dest, os.stat(dest).st_mode | stat.S_IEXEC | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        else:
                print('Please manually copy %s to a local directory and add its path to your system environment variables' % __PROG_NAME__)

setup(
        name=__PROG_NAME__,
        version='1.0.0',
        license=open('LICENSE').read(),
        url='https://github.com/ziggurattech/%s' % __PROG_NAME__,
        author='Fadi Hanna Al-Kass',
        author_email='f_alkass@zgps.live',
        description='General-purpose host deployment utility',
        long_description=open('README.md').read(),
        keywords='deployment automation framework',
        cmdclass={'install': Installer},
        install_requires=open('requirements.txt').read().split('\n'),
)
