import os
from pathlib import Path
import logging
from zdeploy.app import _load_recipes
from zdeploy.config import Config


def test_load_recipes_override(tmp_path):
    cfg = Config(configs=str(tmp_path / "configs"), recipes=str(tmp_path / "recipes"))
    Path(cfg.recipes).mkdir(parents=True)
    (Path(cfg.recipes) / "r1").mkdir()
    (Path(cfg.recipes) / "r2").mkdir()

    cfg_dir = Path(cfg.configs)
    cfg_dir.mkdir(parents=True)
    config1 = cfg_dir / "c1"
    config1.write_text("RECIPES=r1\nr1=1.1.1.1\n")
    config2 = cfg_dir / "c2"
    config2.write_text("RECIPES=r2\nr2=2.2.2.2\n")

    log = logging.getLogger("test_override")

    recipes1 = _load_recipes(config1, log, cfg)
    assert os.environ["RECIPES"] == "r1"
    assert [r.name for r in recipes1] == ["r1"]

    recipes2 = _load_recipes(config2, log, cfg)
    assert os.environ["RECIPES"] == "r2"
    assert [r.name for r in recipes2] == ["r2"]
