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
	cfg['history'] = cfg.get('history', 'history')
	cfg['logs'] = cfg.get('logs', 'logs')
	cfg['installer'] = cfg.get('installer', 'apt-get install -y')

	# The following allows us to use the dot notation to reference the fields, e.g.:
	# cfg.logs instead of cfg['logs']
	return type('', (), cfg)
