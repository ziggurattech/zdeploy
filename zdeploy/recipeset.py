"""Helper for managing sets of ``Recipe`` objects."""

from hashlib import md5
from typing import Iterable

from zdeploy.config import Config
from zdeploy.log import Log
from zdeploy.recipe import Recipe


class RecipeSet(set[Recipe]):
    """Container for ``Recipe`` objects with convenience helpers."""

    def __init__(self, cfg: Config, log: Log) -> None:
        """Create an empty ``RecipeSet`` using ``cfg`` and ``log``."""

        super().__init__()
        self.cfg = cfg
        self.log = log

    def update(self, recipes: Iterable[Recipe]) -> None:  # type: ignore[override]
        """Add a sequence of ``recipes`` to the set."""

        for recipe in recipes:
            self.add(recipe)

    def add(self, recipe: Recipe) -> None:  # type: ignore[override]
        """Add a single ``recipe`` if not already present."""

        if recipe in self:
            self.log.warn(f"Recipe '{recipe.name}' is already added; skipping")
            return
        self.log.info(f"Registering recipe '{recipe.name}'")
        super().add(recipe)
        if recipe.is_virtual():
            self.log.warn(
                (
                    f"Recipe '{recipe.recipe}' is not found under {self.cfg.recipes} "
                    "and will be treated as a system package"
                )
            )
            self.log.warn(
                (
                    f"The package will be installed using `{recipe.cfg.installer} {recipe.recipe}`"
                )
            )
            self.log.warn(
                (
                    "To use a different package manager, specify "
                    "an 'installer' entry in config.json"
                )
            )

    def get_hash(self) -> str:
        """Return an MD5 hash of all recipes combined."""

        return md5(" ".join(str(recipe) for recipe in self).encode()).hexdigest()
