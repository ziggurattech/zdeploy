"""Helper for managing sets of ``Recipe`` objects."""

from hashlib import md5
from typing import Iterable, Iterator, List

from zdeploy.config import Config
from zdeploy.log import Log
from zdeploy.recipe import Recipe


class RecipeSet:
    """
    RecipeSet is a unique set of Recipes maintainer.
    """

    def __init__(self, cfg: Config, log: Log) -> None:
        """Create an empty ``RecipeSet`` using ``cfg`` and ``log``."""

        self.recipes: List[Recipe] = []
        self.cfg = cfg
        self.log = log

    def add_recipes(self, recipes: Iterable[Recipe]) -> None:
        """Add a sequence of ``recipes`` to the set."""

        for recipe in recipes:
            self.add_recipe(recipe)

    def add_recipe(self, recipe: Recipe) -> None:
        """Add a single ``recipe`` if not already present."""

        if recipe in self.recipes:
            self.log.warn(
                f"Recipe '{recipe.get_name()}' is already added; skipping"
            )
            return
        self.log.info(f"Registering recipe '{recipe.get_name()}'")
        self.recipes.append(recipe)
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
        """
        Return an MD5 hash out of the hash of all recipes combined.
        The end result is used to create a cache directory under deployments cache.
        """
        return md5(
            " ".join([str(recipe) for recipe in self.recipes]).encode()
        ).hexdigest()

    def __iter__(self) -> Iterator[Recipe]:
        """
        Allow caller to iterate over recipes with a regular for loop, e.g.:
        for recipe in recipes:
            print(recipe)
        """
        return iter(self.recipes)
