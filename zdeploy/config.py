from json import loads
from os.path import isfile

def load(cfg_path = 'config.json'):
	# Initiate an empty config dictionary in case a config file isn't present
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
	cfg['installer'] = cfg.get('installer', 'apt-get install -y')
	cfg['force'] = cfg.get('force', 'no')

	# Turn cfg into a class allowing us to reference all the field via the dot operator,
	# e.g.: cfg.logs instead of cfg['logs']
	return type('', (), cfg)
