"""Command line interface for zdeploy."""

from argparse import ArgumentParser, Namespace
from os import listdir, makedirs
from os.path import isdir
from sys import stdout
from datetime import datetime

from zdeploy.utils import str2bool

from zdeploy.log import Log
from zdeploy.app import deploy
from zdeploy.config import load as load_config, Config


def handle_config(config_name: str, args: Namespace, cfg: Config) -> None:
    """Deploy a single configuration."""
    log_dir_path = f"{cfg.logs}/{config_name}"
    cache_dir_path = f"{cfg.cache}/{config_name}"
    if not isdir(log_dir_path):
        makedirs(log_dir_path)
    if not isdir(cache_dir_path):
        makedirs(cache_dir_path)
    log = Log()
    log.register_logger(stdout)
    with open(
        f"{log_dir_path}/{datetime.now():%Y-%m-%d %H:%M:%S}.log",
        "w",
        encoding="utf-8",
    ) as log_file:
        log.register_logger(log_file)
        deploy(config_name, cache_dir_path, log, args, cfg)


def handle_configs(args: Namespace, cfg: Config) -> None:
    """Deploy each config provided on the command line."""
    for config_name in args.configs:
        handle_config(config_name, args, cfg)


def main() -> None:
    """CLI entry point."""
    cfg = load_config()
    parser = ArgumentParser()
    parser.add_argument(
        "-c",
        "--configs",
        help="Deployment destination(s)",
        nargs="+",
        required=True,
        choices=listdir(cfg.configs) if isdir(cfg.configs) else (),
    )
    parser.add_argument(
        "-f",
        "--force",
        help="Force full deployment (overlooks the cache)",
        nargs="?",
        required=False,
        default=cfg.force,
        const=True,
        type=str2bool,
    )
    handle_configs(parser.parse_args(), cfg)
