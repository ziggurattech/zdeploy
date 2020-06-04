from argparse import ArgumentParser
from os.path import isdir
from os import listdir, makedirs
from sys import stdout
from datetime import datetime
from zdeploy.log import Log
from zdeploy.app import deploy
from zdeploy.config import load as load_config

def handle_config(config_name, cfg):
    # TODO: document
    log_dir_path = '%s/%s' % (cfg.logs, config_name)
    cache_dir_path = '%s/%s' % (cfg.cache, config_name)
    if not isdir(log_dir_path):
        makedirs(log_dir_path)
    if not isdir(cache_dir_path):
        makedirs(cache_dir_path)
    log = Log()
    log.register_logger(stdout)
    log.register_logger(open('%s/%s.log' % (log_dir_path, '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.now())), 'w'))
    deploy(config_name, cache_dir_path, log, cfg)

def handle_configs(config_names, cfg):
    '''
    Iterate over all retrieved configs and deploy them in a pipelined order.
    '''
    for config_name in config_names:
        handle_config(config_name, cfg)

def main():
    # Default config file name is config.json, so it needs not be specified in our case.
    cfg = load_config()
    parser = ArgumentParser()
    parser.add_argument(
        '-c',
        '--configs',
        help='Deployment destination(s)',
        nargs='+',
        required=True,
        choices=listdir(cfg.configs) if isdir(cfg.configs) else ())
    args = parser.parse_args()
    handle_configs(args.configs, cfg)
