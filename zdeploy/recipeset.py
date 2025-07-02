"""Helper for managing sets of ``Recipe`` objects."""

from hashlib import md5
from zdeploy.recipe import Recipe


class RecipeSet:
    """
    RecipeSet is a unique set of Recipes maintainer.
    """

    def __init__(self, cfg, log):
        """Create an empty ``RecipeSet`` using ``cfg`` and ``log``."""

        self.recipes = []
        self.cfg = cfg
        self.log = log

    def add_recipes(self, recipes):
        """Add a sequence of ``recipes`` to the set."""

        for recipe in recipes:
            self.add_recipe(recipe)

    def add_recipe(self, recipe):
        """Add a single ``recipe`` if not already present."""

        if recipe in self.recipes:
            self.log.warn(
                f"{recipe.get_name()} is already added to the recipes list. Skipping..."
            )
            return
        self.log.info(f"Adding '{recipe.get_name()}' to the recipes list")
        self.recipes.append(recipe)
        if recipe._type == Recipe.Type.VIRTUAL:
            self.log.warn(
                (
                    f"'{recipe.recipe}' doesn't correspond to anything defined "
                    f"under the {self.cfg.recipes} directory"
                )
            )
            self.log.warn(
                (
                    "this recipe will be marked virtual and execute as "
                    f"`{recipe.cfg.installer} {recipe.recipe}`"
                )
            )
            self.log.warn(
                (
                    "If you want to use a different package manager, add an "
                    "'installer' field to the config.json file"
                )
            )

    def get_hash(self):
        """
        Return an MD5 hash out of the hash of all recipes combined.
        The end result is used to create a cache directory under deployments cache.
        """
        return md5(
            " ".join([str(recipe) for recipe in self.recipes]).encode()
        ).hexdigest()

    def __iter__(self):
        """
        Allow caller to iterate over recipes with a regular for loop, e.g.:
        for recipe in recipes:
            print(recipe)
        """
        return iter(self.recipes)
