"""Helper for managing sets of ``Recipe`` objects."""

from hashlib import md5
from typing import Iterable
import logging

from zdeploy.config import Config
from zdeploy.recipe import Recipe


class RecipeSet(set[Recipe]):
    """Container for ``Recipe`` objects with convenience helpers."""

    def __init__(self, cfg: Config, log: logging.Logger) -> None:
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
            self.log.warning("Recipe '%s' is already added; skipping", recipe.name)
            return
        self.log.info("Registering recipe '%s'", recipe.name)
        super().add(recipe)
        if recipe.is_virtual():
            self.log.warning(
                (
                    f"Recipe '{recipe.recipe}' is not found under {self.cfg.recipes} "
                    "and will be treated as a system package"
                )
            )
            self.log.warning(
                (
                    f"The package will be installed using `{recipe.cfg.installer} {recipe.recipe}`"
                )
            )
            self.log.warning(
                (
                    "To use a different package manager, specify "
                    "an 'installer' entry in config.json"
                )
            )

    def get_hash(self) -> str:
        """Return an MD5 hash of all recipes combined."""

        return md5(" ".join(str(recipe) for recipe in self).encode()).hexdigest()
