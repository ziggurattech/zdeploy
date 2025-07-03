from zdeploy import config

def test_load_defaults(tmp_path):
    cfg = config.load(str(tmp_path / 'missing.json'))
    assert cfg.configs == 'configs'
    assert cfg.recipes == 'recipes'
    assert cfg.cache == 'cache'
    assert cfg.logs == 'logs'
    assert cfg.force is False
