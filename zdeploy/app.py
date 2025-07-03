"""Deployment core logic."""

from os import environ
from pathlib import Path
from shutil import rmtree
from datetime import datetime
from argparse import Namespace
import logging

from dotenv import load_dotenv
from zdeploy.recipe import Recipe
from zdeploy.recipeset import RecipeSet
from zdeploy.utils import reformat_time
from zdeploy.config import Config


def _load_recipes(config_path: Path, log: logging.Logger, cfg: Config) -> RecipeSet:
    """Return a ``RecipeSet`` loaded from environment variables."""

    # Ensure variables from previous configs do not linger
    # when deploying multiple configs sequentially.
    load_dotenv(str(config_path), override=True)

    recipes = RecipeSet(cfg, log)
    recipe_names = environ.get("RECIPES", "")
    if recipe_names.startswith("(") and recipe_names.endswith(")"):
        recipe_names = recipe_names[1:-1]
    for recipe_name in recipe_names.split(" "):
        recipe_name = recipe_name.strip()
        host_ip = environ.get(recipe_name)
        if host_ip is None:
            log.error(f"{recipe_name} is undefined in {config_path}")
            raise RuntimeError("undefined host")
        host_user = environ.get(f"{recipe_name}_USER", cfg.user)
        host_password = environ.get(f"{recipe_name}_PASSWORD", cfg.password)
        host_port_str = environ.get(f"{recipe_name}_PORT")
        host_port = int(host_port_str) if host_port_str is not None else cfg.port

        recipe = Recipe(
            recipe_name,
            None,
            config_path,
            host_ip,
            host_user,
            host_password,
            host_port,
            log,
            cfg,
        )

        for env in environ:
            if env.startswith(recipe_name) and env != recipe_name:
                recipe.set_property(env, environ.get(env))

        recipes.update(recipe.load_requirements())
        recipes.add(recipe)

    return recipes


def _clean_cache(cache_dir_path: Path, deployment_cache_path: Path, log: logging.Logger) -> None:
    """Remove stale cache directories inside ``cache_dir_path``."""

    if not deployment_cache_path.is_dir():
        deployment_cache_path.mkdir(parents=True)
    for directory in cache_dir_path.iterdir():
        if directory != deployment_cache_path:
            log.info(f"Removing stale cache directory {directory}")
            rmtree(directory)


def _deploy_recipe(
    recipe: Recipe,
    deployment_cache_path: Path,
    force: bool,
    started_all: datetime,
    log: logging.Logger,
) -> None:
    """Deploy a single ``recipe`` and update its cache entry."""

    recipe_cache_path = deployment_cache_path / recipe.name
    if recipe_cache_path.is_file():
        with recipe_cache_path.open("r", encoding="utf-8") as fp:
            cache_contents = fp.read()
        if recipe.deep_hash() in cache_contents and not force:
            log.warning(
                f"Skipping {recipe.name} because it is already deployed"
            )
            return

    started_recipe = datetime.now()
    log.info(
        f"Starting recipe '{recipe.name}' at "
        f"{started_recipe:%H:%M:%S} on {started_all:%Y-%m-%d}"
    )
    recipe.deploy()
    ended_recipe = datetime.now()
    log.info(
        f"Finished recipe '{recipe.name}' at "
        f"{ended_recipe:%H:%M:%S} on {started_all:%Y-%m-%d}"
    )

    total_recipe_time = ended_recipe - started_recipe
    log.info(f"{recipe.name} finished in {reformat_time(total_recipe_time)}")
    with recipe_cache_path.open("w", encoding="utf-8") as fp:
        fp.write(recipe.deep_hash())


def deploy(
    config_name: str,
    cache_dir_path: Path,
    log: logging.Logger,
    args: Namespace,
    cfg: Config,
) -> None:
    """Deploy recipes defined in ``config_name``."""

    config_path = Path(cfg.configs) / config_name
    log.info("Config: %s", config_path)

    recipes = _load_recipes(config_path, log, cfg)

    started_all = datetime.now()
    log.info(
        f"Starting deployment of {config_path} at {started_all:%H:%M:%S} on {started_all:%Y-%m-%d}"
    )

    deployment_cache_path = cache_dir_path / recipes.get_hash()
    _clean_cache(cache_dir_path, deployment_cache_path, log)

    for recipe in recipes:
        _deploy_recipe(recipe, deployment_cache_path, args.force, started_all, log)

    ended_all = datetime.now()
    total_deployment_time = ended_all - started_all
    log.info(
        f"Completed deployment of {config_path} at {ended_all:%H:%M:%S} on {started_all:%Y-%m-%d}"
    )
    log.info(f"{config_path} finished in {reformat_time(total_deployment_time)}")
    log.info(f"Deployment hash is {recipes.get_hash()}")
