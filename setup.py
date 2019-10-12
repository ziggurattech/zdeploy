from setuptools import setup
from setuptools.command.install import install
import os

class Installer(install):
    def run(self):
        print(os.popen('cp zdeploy /usr/bin/').read())

setup(
        name='zdeploy',
        url='https://github.com/ziggurattech/zdeploy',
        author='Fadi Hanna Al-Kass',
        description='General-purpose host deployment utility',
        long_description=open('README.md').read(),
        cmdclass={'install': Installer},
        install_requires=[
            'paramiko',
            'requests',
            'python-dotenv',
        ],
        dependency_links=[
            'git+https://github.com/jbardin/scp.py/tarball/master',
        ],
)
