from json import loads
from os.path import isfile

def load(cfg_path = 'config.json'):
	# Initiate an empty config dictionary in case a config
	# file isn't present.
	cfg = {}

	if isfile(cfg_path):
		# Load data in JSON form.
		# TODO: try..catch with an informative exception
		cfg = loads(open(cfg_path).read())

	# Set defaults
	cfg['configs'] = cfg.get('configs', 'configs')
	cfg['recipes'] = cfg.get('recipes', 'recipes')
	cfg['cache'] = cfg.get('cache', 'cache')
	cfg['logs'] = cfg.get('logs', 'logs')

	# Default installer is apt-get. This is used for virtual
	# recipes (recipes that aren't defined by a directory
	# structure).
	cfg['installer'] = cfg.get('installer', 'apt-get install -y')
	
	# Force is disabled by default. This sets the behavior to
	# only deploy undeployed recipes and/or pick up where a
	# previous deployment was halted or had crashed.
	cfg['force'] = cfg.get('force', 'no')
	
	# Default username is root
	cfg['user'] = cfg.get('user', 'root')

	# The default is no password (private key present)
	cfg['password'] = cfg.get('password', None)
	
	cfg['port'] = cfg.get('port', 22)

	# Turn cfg into a class allowing us to reference all the field via the dot operator,
	# e.g.: cfg.logs instead of cfg['logs']
	return type('', (), cfg)
