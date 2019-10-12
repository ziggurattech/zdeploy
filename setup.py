from setuptools import setup
from setuptools.command.install import install
import os

class Installer(install):
    def run(self):
        cmds = [
            'pip install -r requirements.txt',
            'cp zdeploy /bin/',
        ]
        for cmd in cmds:
            print('Running', cmd)
            res = os.popen(cmd).read()
            print(res)

setup(cmdclass={'install': Installer})