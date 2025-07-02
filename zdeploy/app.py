"""Deployment core logic."""

from os import listdir, makedirs, environ
from os.path import isdir, isfile
from shutil import rmtree
from datetime import datetime
from dotenv import load_dotenv
from zdeploy.recipe import Recipe
from zdeploy.recipeset import RecipeSet
from zdeploy.utils import reformat_time


def deploy(config_name, cache_dir_path, log, args, cfg):
    """Deploy recipes defined in ``config_name``."""
    config_path = f"{cfg.configs}/{config_name}"
    print("Config:", config_path)
    load_dotenv(config_path)

    recipes = RecipeSet(cfg, log)

    recipe_names = environ.get("RECIPES", "")
    if recipe_names.startswith("(") and recipe_names.endswith(")"):
        recipe_names = recipe_names[1:-1]
    for recipe_name in recipe_names.split(" "):
        recipe_name = recipe_name.strip()
        HOST_IP = environ.get(recipe_name)
        if HOST_IP is None:
            log.fatal(f"{recipe_name} is undefined in {config_path}")
        HOST_USER = environ.get(f"{recipe_name}_USER", cfg.user)
        HOST_PASSWORD = environ.get(f"{recipe_name}_PASSWORD", cfg.password)
        HOST_PORT = environ.get(f"{recipe_name}_PORT", cfg.port)
        recipe = Recipe(
            recipe_name,
            None,
            config_path,
            HOST_IP,
            HOST_USER,
            HOST_PASSWORD,
            HOST_PORT,
            log,
            cfg,
        )
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
    log.info(
        f"Started {config_path} deployment at {started_all:%H:%M:%S} on {started_all:%Y-%m-%d}"
    )
    deployment_cache_path = f"{cache_dir_path}/{recipes.get_hash()}"
    if not isdir(deployment_cache_path):
        makedirs(deployment_cache_path)
    for dir in listdir(cache_dir_path):
        # Delete all stale cache tracks so we don't run into issues
        # when reverting deployments.
        dir = f"{cache_dir_path}/{dir}"
        if dir != deployment_cache_path:
            log.info(f"Deleting {dir}")
            rmtree(dir)
    for recipe in recipes:
        recipe_cache_path = f"{deployment_cache_path}/{recipe.get_name()}"
        if (
            isfile(recipe_cache_path)
            and recipe.get_deep_hash() in open(recipe_cache_path, "r", encoding="utf-8").read()
            and not args.force
        ):
            log.warn(f"{recipe.get_name()} is already deployed. Skipping...")
            continue
        started_recipe = datetime.now()
        log.info(
            f"Started {recipe.get_name()} recipe deployment at "
            f"{started_recipe:%H:%M:%S} on {started_all:%Y-%m-%d}"
        )
        recipe.deploy()
        ended_recipe = datetime.now()
        log.info(
            f"Ended {recipe.get_name()} recipe deployment at "
            f"{ended_recipe:%H:%M:%S} on {started_all:%Y-%m-%d}"
        )
        total_recipe_time = ended_recipe - started_recipe
        log.success(
            f"{recipe.get_name()} finished in {reformat_time(total_recipe_time)}"
        )
        with open(recipe_cache_path, "w", encoding="utf-8") as fp:
            fp.write(recipe.get_deep_hash())
    ended_all = datetime.now()
    total_deployment_time = ended_all - started_all
    log.info(
        f"Ended {config_path} deployment at {ended_all:%H:%M:%S} on {started_all:%Y-%m-%d}"
    )
    log.success(
        f"{config_path} finished in {reformat_time(total_deployment_time)}"
    )
    log.info(f"Deployment hash is {recipes.get_hash()}")
