from os import listdir, makedirs, environ
from os.path import isdir, isfile
from shutil import rmtree
from datetime import datetime
from dotenv import load_dotenv
from zdeploy.recipe import Recipe
from zdeploy.recipeset import RecipeSet

def deploy(config_name, cache_dir_path, log, args, cfg):
    config_path = '%s/%s' % (cfg.configs, config_name)
    print('Config:', config_path)
    load_dotenv(config_path)

    recipes = RecipeSet(cfg, log)

    recipe_names = environ.get('RECIPES')
    if recipe_names.startswith('(') and recipe_names.endswith(')'):
        recipe_names = recipe_names[1:-1]
    for recipe_name in recipe_names.split(' '):
        recipe_name = recipe_name.strip()
        HOST_IP = environ.get(recipe_name)
        if HOST_IP is None:
            log.fatal('%s is undefined in %s' % (recipe_name, config_path))
        HOST_USER = environ.get('%s_USER' % recipe_name, 'root')
        recipe = Recipe(recipe_name, None, config_path, HOST_IP, HOST_USER, log, cfg)
        for env in environ:
            if env.startswith(recipe_name) and env != recipe_name:
                # Properties aren't used anywhere internally. We only
                # monitor them so hashes are generated properly. That
                # said, if a recipe-name-related environment variable
                # changes, we should assume a level of relevancy at
                # the recipe level.
                recipe.set_property(env, environ.get(env))
        recipes.add_recipes(recipe.get_requirements())
        recipes.add_recipe(recipe)

    started_all = datetime.now()
    log.info('Started %s deployment at %s on %s' % 
        (config_path,
        started_all.strftime('%H:%M:%S'),
        started_all.strftime('%Y-%m-%d')))
    deployment_cache_path = '%s/%s' % (cache_dir_path, recipes.get_hash())
    if not isdir(deployment_cache_path):
        makedirs(deployment_cache_path)
    for dir in listdir(cache_dir_path):
        # Delete all stale cache tracks so we don't run into issues
        # when reverting deployments.
        dir = '%s/%s' % (cache_dir_path, dir)
        if dir != deployment_cache_path:
            log.info('Deleting %s' % dir)
            rmtree(dir)
    for recipe in recipes:
        recipe_cache_path = '%s/%s' % (deployment_cache_path, recipe.get_name())
        if isfile(recipe_cache_path) and recipe.get_deep_hash() in open(recipe_cache_path, 'r').read() and not args.force:
            log.warn('%s is already deployed. Skipping...' % recipe.get_name())
            continue
        started_recipe = datetime.now()
        log.info('Started %s recipe deployment at %s on %s' %
            (recipe.get_name(),
            started_recipe.strftime('%H:%M:%S'),
            started_all.strftime('%Y-%m-%d')))
        recipe.deploy()
        ended_recipe = datetime.now()
        log.info('Ended %s recipe deployment at %s on %s' %
        (recipe.get_name(),
        ended_recipe.strftime('%H:%M:%S'),
        started_all.strftime('%Y-%m-%d')))
        total_recipe_time = ended_recipe - started_recipe
        log.success('%s finished in %s' % (recipe.get_name(), total_recipe_time))
        open(recipe_cache_path, 'w').write(recipe.get_deep_hash())
    ended_all = datetime.now()
    total_deployment_time = ended_all - started_all
    log.info('Ended %s deployment at %s on %s' %
        (config_path,
        ended_all.strftime('%H:%M:%S'),
        started_all.strftime('%Y-%m-%d')))
    log.success('%s finished in %s' % (config_path, total_deployment_time))
    log.info('Deployment hash is %s' % recipes.get_hash())
