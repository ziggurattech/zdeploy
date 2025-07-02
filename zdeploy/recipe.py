"""Recipe abstraction for deploying and tracking dependencies."""
# pylint: disable=too-many-instance-attributes,too-few-public-methods,too-many-arguments,too-many-positional-arguments

from os import listdir
from pathlib import Path
from hashlib import md5
from typing import Dict, List, Optional

from zdeploy.clients import SSH, SCP
from zdeploy.shell import execute as shell_execute
from zdeploy.log import Log
from zdeploy.config import Config


class Recipe:
    """Represents a deployable script or package."""

    class Type:
        """Supported recipe types."""

        DEFINED = 1
        VIRTUAL = 2

    def __init__(
        self,
        recipe: str,
        parent_recipe: Optional[str],
        config: Path,
        hostname: str,
        username: str,
        password: str | None,
        port: int,
        log: Log,
        cfg: Config,
    ) -> None:
        """Initialize a recipe instance."""

        self.log = log
        if not str(config).strip():
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
        self._resolve_name_and_type(recipe)
        self.config = config
        self.hostname = hostname
        self.username = username
        self.password = password
        self.properties: Dict[str, str | None] = {}

    def set_property(self, key: str, value: str | None) -> None:
        """Store an arbitrary ``key``/``value`` pair."""

        self.properties[key] = value

    def _resolve_name_and_type(self, recipe: str) -> None:
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

    def __str__(self) -> str:
        """Return a string representation of this recipe."""

        return f"{self.recipe} -> {self.username}@{self.hostname}:{self.port} :: {self.properties}"

    @property
    def name(self) -> str:
        """Return the recipe name."""

        return self.recipe

    def __hash__(self) -> int:
        """Return a hash so recipes can be used in sets and dictionaries."""

        return hash(str(self))

    def __eq__(self, other: object) -> bool:
        """Compare recipes by their hash."""

        return hash(self) == hash(other)

    def is_virtual(self) -> bool:
        """Return ``True`` if this is a virtual recipe."""

        return self._type == self.Type.VIRTUAL

    def deep_hash(self, dir_path: Path | None = None) -> str:
        """Return an MD5 hash representing the recipe and its requirements."""

        hashes = ""
        if self._type == self.Type.VIRTUAL:
            hashes = md5(self.recipe.encode()).hexdigest()
        elif self._type == self.Type.DEFINED:
            if dir_path is None:
                dir_path = Path(self.cfg.recipes) / self.recipe

                # Execute the hash script and copy its output into our hashes variable.
                # NOTE: We perform this check specifically inside this block because when
                # dir_path is None, we know we're at the main recipe directory path.
                hash_path = dir_path / "hash"
                if hash_path.is_file():
                    cmd_out, cmd_rc = shell_execute(
                        f"chmod +x {hash_path} && bash {self.config} && ./{hash_path}"
                    )
                    if cmd_rc != 0:
                        raise RuntimeError(cmd_out)
                    hashes += cmd_out

            for recipe in self.load_requirements():
                hashes += recipe.deep_hash()
            hashes += md5(str(self).encode()).hexdigest()
            for node in listdir(dir_path):
                rel_path = dir_path / node
                if rel_path.is_file():
                    with rel_path.open("rb") as fp:
                        file_hash = md5(fp.read()).hexdigest()
                    hashes += file_hash
                elif rel_path.is_dir():
                    hashes += self.deep_hash(rel_path)
        return md5(hashes.encode()).hexdigest()

    def load_requirements(self) -> List["Recipe"]:
        """Return a list of Recipe objects this recipe depends on."""

        req_file = Path(self.cfg.recipes) / self.recipe / "require"
        requirements: List["Recipe"] = []
        if req_file.is_file():
            with req_file.open("r", encoding="utf-8") as req_fp:
                for requirement in req_fp.read().split("\n"):
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
                    for req in recipe.load_requirements():
                        requirements.append(req)
                    requirements.append(recipe)
        return requirements

    def deploy(self) -> None:
        """Deploy this recipe using SSH/SCP."""

        self.log.info(f"Deploying '{self.recipe}' to {self.hostname}")
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

            transport = ssh.get_transport()
            assert transport is not None
            scp = SCP(transport)
            scp.put(
                str(Path(self.cfg.recipes) / self.recipe),
                remote_path=f"/opt/{self.recipe}",
                recursive=True,
            )
            scp.put(str(self.config), remote_path=f"/opt/{self.recipe}/config")

        try:
            if self._type == self.Type.VIRTUAL:
                ssh.execute(f"{self.cfg.installer} {self.recipe}")
            elif self._type == self.Type.DEFINED:
                if not (Path(self.cfg.recipes) / self.recipe / "run").is_file():
                    # Recipes with no run file are acceptable since they (may) have a require file
                    # and don't necessarily require the execution of anything of their own.
                    self.log.warn(
                        f"Recipe '{self.recipe}' has no run file; continuing"
                    )
                else:
                    ssh.execute(
                        f"cd /opt/{self.recipe} && chmod +x ./run && ./run",
                        show_command=False,
                    )
            passed = True
        except Exception as exc:  # pylint: disable=broad-except
            self.log.fail(str(exc))
            passed = False
        finally:
            if self._type == self.Type.DEFINED:
                self.log.info(f"Removing /opt/{self.recipe} from remote host")
                ssh.execute(f"rm -rf /opt/{self.recipe}", show_command=False)

        if not passed:
            self.log.fatal(f"Failed to deploy {self.recipe}")
        self.log.success(f"Done with {self.recipe}")
