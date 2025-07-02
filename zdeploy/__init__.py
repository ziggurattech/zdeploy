"""Command line interface for zdeploy."""

from argparse import ArgumentParser, Namespace
from datetime import datetime
from os import listdir
from pathlib import Path
from sys import stdout

from zdeploy.utils import str2bool

from zdeploy.log import Log
from zdeploy.app import deploy
from zdeploy.config import load as load_config, Config

log = Log()
log.register_logger(stdout)


def deploy_config(config_name: str, args: Namespace, cfg: Config) -> None:
    """Deploy a single configuration."""
    log_dir_path = Path(cfg.logs) / config_name
    cache_dir_path = Path(cfg.cache) / config_name
    if not log_dir_path.is_dir():
        log_dir_path.mkdir(parents=True)
    if not cache_dir_path.is_dir():
        cache_dir_path.mkdir(parents=True)
    log_file_path = log_dir_path / f"{datetime.now():%Y-%m-%d %H:%M:%S}.log"
    with log_file_path.open("w", encoding="utf-8") as log_file:
        log.register_logger(log_file)
        deploy(config_name, cache_dir_path, log, args, cfg)
        log.loggers.remove(log_file)


def deploy_configs(args: Namespace, cfg: Config) -> None:
    """Deploy each config provided on the command line."""
    for config_name in args.configs:
        deploy_config(config_name, args, cfg)


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
        choices=listdir(cfg.configs) if Path(cfg.configs).is_dir() else (),
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
    deploy_configs(parser.parse_args(), cfg)
