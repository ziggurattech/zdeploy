from setuptools import setup
from setuptools.command.install import install
import os

class Installer(install):
    def run(self):
        print(os.popen('make').read())

setup(
        cmdclass={'install': Installer},
        install_requires=[
            'paramiko',
            'requests',
            'python-dotenv',
            'git+https://github.com/jbardin/scp.py',
        ],
)
