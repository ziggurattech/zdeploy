from hashlib import md5
from zdeploy.recipe import Recipe

class RecipeSet:
    '''
        RecipeSet is a unique set of Recipes maintainer.
    '''
    def __init__(self, cfg, log):
        self.recipes = []
        self.cfg = cfg
        self.log = log
    def add_recipes(self, recipes):
        for recipe in recipes:
            self.add_recipe(recipe)
    def add_recipe(self, recipe):
        if recipe in self.recipes:
            self.log.warn('%s is already added to recipes. Skipping...' % recipe.get_name())
            return
        self.log.info('Adding %s to recipes list' % recipe.get_name())
        self.recipes.append(recipe)
        if recipe._type == Recipe.Type.VIRTUAL:
            self.log.warn("'%s' doesn't correspond to anything defined under the %s directory" % (recipe.recipe, self.cfg.recipes))
            self.log.warn('%s will be marked virtual and execute as %s %s' % (recipe.recipe, recipe.cfg.installer, recipe.recipe))
            self.log.warn("If you want to use a different package manager, add an 'installer' field to your config.json file")
    def get_hash(self):
        '''
        Return an MD5 hash out of the hash of all recipes combined.
        The end result is used to create a cache directory under deployments cache.
        '''
        return md5(' '.join([str(recipe) for recipe in self.recipes]).encode()).hexdigest()
    def __iter__(self):
        '''
        Allow caller to iterate over recipes with a regular for loop, e.g.:
        for recipe in recipes:
            print(recipe)
        '''
        return iter(self.recipes)
