from os import listdir
from os.path import isdir, isfile
from datetime import datetime
from hashlib import md5
from zdeploy.clients import SSH, SCP

class Recipe:
    class Type:
        DEFINED = 1
        VIRTUAL = 2
    def __init__(self, recipe, parent_recipe, config, hostname, username, log, cfg):
        self.log = log
        if not config or not len(config.strip()):
            self.log.fatal('Invalid value for config')
        if not recipe or not len(recipe.strip()):
            self.log.fatal('Invalid value for recipe')
        if not hostname or not len(hostname.strip()):
            self.log.fatal('Invalid value for hostname')
        self.cfg = cfg
        self.parent_recipe = parent_recipe
        self.set_recipe_name_and_type(recipe)
        self.config = config
        self.hostname = hostname
        self.username = username
        self.properties = {}
    def set_property(self, key, value):
        self.properties[key] = value
    def set_recipe_name_and_type(self, recipe):
        for r in listdir(self.cfg.recipes):
            if recipe.lower() == r.lower():
                self.recipe = r
                if self.parent_recipe == r:
                    # Recipe references itself
                    self.log.fatal('Invalid recipe: %s references itself' % r)
                else:
                    self._type = self.Type.DEFINED
                return
        self.recipe = recipe
        self._type = self.Type.VIRTUAL
    def __str__(self):
        return '%s -> %s:%s :: %s' % (self.recipe, self.username, self.hostname, self.properties)
    def get_name(self):
        return self.recipe
    def __hash__(self):
        return hash(str(self))
    def __eq__(self, other):
        return hash(self) == hash(other)
    def get_deep_hash(self, dir_path=None):
        hashes = ''
        if self._type == self.Type.VIRTUAL:
            hashes = md5(self.recipe.encode()).hexdigest()
        elif self._type == self.Type.DEFINED:
            if dir_path is None:
                dir_path = '%s/%s' % (self.cfg.recipes, self.recipe)
            for recipe in self.get_requirements():
                hashes += recipe.get_deep_hash()
            hashes += md5(str(self).encode()).hexdigest()
            for node in listdir(dir_path):
                rel_path = '%s/%s' % (dir_path, node)
                if isfile(rel_path):
                    file_hash = md5(open(rel_path, 'rb').read()).hexdigest()
                    hashes += file_hash
                elif isdir(rel_path):
                    hashes += self.get_deep_hash(rel_path)
        return md5(hashes.encode()).hexdigest()
    def get_requirements(self):
        req_file = '%s/%s/require' % (self.cfg.recipes, self.recipe)
        requirements = []
        if isfile(req_file):
            for requirement in open(req_file).read().split('\n'):
                requirement = requirement.strip()
                if requirement == '' or requirement.startswith('#'):
                    continue
                recipe = Recipe(
                    recipe=requirement,
                    parent_recipe=self.recipe,
                    config=self.config,
                    hostname=self.hostname,
                    username=self.username,
                    log=self.log,
                    cfg=self.cfg)
                for req in recipe.get_requirements():
                    requirements.append(req)
                requirements.append(recipe)
        return requirements
    def deploy(self):
        self.log.info('Deploying %s to %s' % (self.recipe, self.hostname))
        ssh = SSH(recipe=self.recipe, log=self.log, hostname=self.hostname, username=self.username)

        if self._type == self.Type.DEFINED:
            ssh.execute('rm -rf /opt/%s' % self.recipe, show_command=False)

            scp = SCP(ssh.get_transport())
            scp.put('%s/%s' % (self.cfg.recipes, self.recipe), remote_path='/opt/%s' % self.recipe, recursive=True)
            scp.put(self.config, remote_path='/opt/%s/config' % self.recipe)

        try:
            if self._type == self.Type.VIRTUAL:
                ssh.execute('%s %s' % (self.cfg.installer, self.recipe))
            elif self._type == self.Type.DEFINED:
                ssh.execute('cd /opt/%s && chmod +x ./run && ./run' % self.recipe, show_command=False)
            passed = True
        except Exception:
            passed = False
        finally:
            if self._type == self.Type.DEFINED:
                self.log.info('Deleting /opt/%s from remote host' % self.recipe)
                ssh.execute('rm -rf /opt/%s' % self.recipe, show_command=False)

        if not passed:
            self.log.fatal('Failed to deploy %s' % self.recipe)
        self.log.success('Done with %s' % self.recipe)
