import zdeploy.recipe as recipe_mod
from zdeploy.recipeset import RecipeSet
from zdeploy.log import Log
from zdeploy.config import Config


def test_recipeset_iterable(tmp_path):
    cfg = Config(recipes=str(tmp_path))
    log = Log()
    r = recipe_mod.Recipe(
        "pkg1",
        None,
        tmp_path / "cfg",
        "host",
        "user",
        None,
        22,
        log,
        cfg,
    )
    rs = RecipeSet(cfg, log)
    rs.add(r)
    for item in rs:
        assert item is r
    assert len(list(rs)) == 1
