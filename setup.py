from setuptools import setup
from setuptools.command.install import install
import os

class Installer(install):
    def run(self):
        print(os.popen('cp zdeploy /usr/bin/').read())

setup(
        cmdclass={'install': Installer},
        install_requires=[
            'paramiko',
            'requests',
            'python-dotenv',
        ],
        dependency_links=[
            'git+git://github.com/jbardin/scp.py',
        ],
)
