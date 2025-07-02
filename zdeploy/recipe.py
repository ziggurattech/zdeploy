"""Recipe abstraction for deploying and tracking dependencies."""

from os import listdir
from os.path import isdir, isfile
from hashlib import md5
from zdeploy.clients import SSH, SCP
from zdeploy.shell import execute as shell_execute


class Recipe:
    """Represents a deployable script or package."""

    class Type:
        """Supported recipe types."""

        DEFINED = 1
        VIRTUAL = 2

    def __init__(
        self,
        recipe,
        parent_recipe,
        config,
        hostname,
        username,
        password,
        port,
        log,
        cfg,
    ):
        """Initialize a recipe instance."""

        self.log = log
        if not config or not config.strip():
            self.log.fatal("Invalid value for config")
        if not recipe or not recipe.strip():
            self.log.fatal("Invalid value for recipe")
        if not hostname or not hostname.strip():
            self.log.fatal("Invalid value for hostname")
        try:
            self.port = int(port)
        except ValueError:
            self.log.fatal(f"Invalid value for port: {port}")

        self.cfg = cfg
        self.parent_recipe = parent_recipe
        self.set_recipe_name_and_type(recipe)
        self.config = config
        self.hostname = hostname
        self.username = username
        self.password = password
        self.properties = {}

    def set_property(self, key, value):
        """Store an arbitrary ``key``/``value`` pair."""

        self.properties[key] = value

    def set_recipe_name_and_type(self, recipe):
        """Resolve ``recipe`` name and determine if it is defined or virtual."""

        for r in listdir(self.cfg.recipes):
            if recipe.lower() == r.lower():
                self.recipe = r
                if self.parent_recipe == r:
                    # Recipe references itself
                    self.log.fatal(f"Invalid recipe: {r} references itself")
                else:
                    self._type = self.Type.DEFINED
                return
        self.recipe = recipe
        self._type = self.Type.VIRTUAL

    def __str__(self):
        """Return a string representation of this recipe."""

        return f"{self.recipe} -> {self.username}@{self.hostname}:{self.port} :: {self.properties}"

    def get_name(self):
        """Return the recipe name."""

        return self.recipe

    def __hash__(self):
        """Return a hash so recipes can be used in sets and dictionaries."""

        return hash(str(self))

    def __eq__(self, other):
        """Compare recipes by their hash."""

        return hash(self) == hash(other)

    def get_deep_hash(self, dir_path=None):
        """Return an MD5 hash representing the recipe and its requirements."""

        hashes = ""
        if self._type == self.Type.VIRTUAL:
            hashes = md5(self.recipe.encode()).hexdigest()
        elif self._type == self.Type.DEFINED:
            if dir_path is None:
                dir_path = f"{self.cfg.recipes}/{self.recipe}"

                # Execute the hash script and copy its output into our hashes variable.
                # NOTE: We perform this check specifically inside this block because when
                # dir_path is None, we know we're at the main recipe directory path.
                if isfile(f"{dir_path}/hash"):
                    cmd_out, cmd_rc = shell_execute(
                        f"chmod +x {dir_path}/hash && bash {self.config} && ./{dir_path}/hash"
                    )
                    if cmd_rc != 0:
                        raise Exception(cmd_out)
                    hashes += cmd_out

            for recipe in self.get_requirements():
                hashes += recipe.get_deep_hash()
            hashes += md5(str(self).encode()).hexdigest()
            for node in listdir(dir_path):
                rel_path = f"{dir_path}/{node}"
                if isfile(rel_path):
                    file_hash = md5(open(rel_path, "rb").read()).hexdigest()
                    hashes += file_hash
                elif isdir(rel_path):
                    hashes += self.get_deep_hash(rel_path)
        return md5(hashes.encode()).hexdigest()

    def get_requirements(self):
        """Return a list of Recipe objects this recipe depends on."""

        req_file = f"{self.cfg.recipes}/{self.recipe}/require"
        requirements = []
        if isfile(req_file):
            for requirement in open(req_file).read().split("\n"):
                requirement = requirement.strip()
                if requirement == "" or requirement.startswith("#"):
                    continue
                recipe = Recipe(
                    recipe=requirement,
                    parent_recipe=self.recipe,
                    config=self.config,
                    hostname=self.hostname,
                    username=self.username,
                    password=self.password,
                    port=self.port,
                    log=self.log,
                    cfg=self.cfg,
                )
                for req in recipe.get_requirements():
                    requirements.append(req)
                requirements.append(recipe)
        return requirements

    def deploy(self):
        """Deploy this recipe using SSH/SCP."""

        self.log.info(f"Deploying {self.recipe} to {self.hostname}")
        ssh = SSH(
            recipe=self.recipe,
            log=self.log,
            hostname=self.hostname,
            username=self.username,
            password=self.password,
            port=self.port,
        )

        if self._type == self.Type.DEFINED:
            ssh.execute(f"rm -rf /opt/{self.recipe}", show_command=False)

            scp = SCP(ssh.get_transport())
            scp.put(
                f"{self.cfg.recipes}/{self.recipe}",
                remote_path=f"/opt/{self.recipe}",
                recursive=True,
            )
            scp.put(self.config, remote_path=f"/opt/{self.recipe}/config")

        try:
            if self._type == self.Type.VIRTUAL:
                ssh.execute(f"{self.cfg.installer} {self.recipe}")
            elif self._type == self.Type.DEFINED:
                if not isfile(f"{self.cfg.recipes}/{self.recipe}/run"):
                    # Recipes with no run file are acceptable since they (may) have a require file
                    # and don't necessarily require the execution of anything of their own.
                    self.log.warn(
                        f"{self.recipe} doesn't have a run file. Continuing..."
                    )
                else:
                    ssh.execute(
                        f"cd /opt/{self.recipe} && chmod +x ./run && ./run",
                        show_command=False,
                    )
            passed = True
        except Exception:
            passed = False
        finally:
            if self._type == self.Type.DEFINED:
                self.log.info(f"Deleting /opt/{self.recipe} from remote host")
                ssh.execute(f"rm -rf /opt/{self.recipe}", show_command=False)

        if not passed:
            self.log.fatal(f"Failed to deploy {self.recipe}")
        self.log.success(f"Done with {self.recipe}")
