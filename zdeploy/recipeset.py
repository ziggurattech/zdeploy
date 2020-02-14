from hashlib import md5
from zdeploy.recipe import Recipe

class RecipeSet:
    recipes = []
    def __init__(self, cfg):
        self.cfg = cfg
    def set_logger(self, log):
        self.log = log
    def add_recipes(self, recipes):
        for recipe in recipes:
            self.add_recipe(recipe)
    def add_recipe(self, recipe):
        if recipe in self.recipes:
            self.log.warn('%s already added to recipes. Skipping...' % recipe.get_name())
            return
        self.log.info('Adding %s to recipes list' % recipe.get_name())
        self.recipes.append(recipe)

        if recipe._type == Recipe.Type.VIRTUAL:
            self.log.warn("Recipe %s doesn't correspond to anything defined under the %s directory" % (recipe.recipe, self.cfg.recipes))
            self.log.warn('%s will be marked virtual and execute as %s' % (recipe.recipe, recipe.command))
            self.log.warn('If you want to use a different package manager, add an "installer" field to your config.json file')
    def get_hash(self):
        return md5(' '.join([str(recipe) for recipe in self.recipes]).encode()).hexdigest()
    def __iter__(self):
        return iter(self.recipes)