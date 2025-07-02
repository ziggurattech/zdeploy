import zdeploy.utils as utils

def test_reformat_time():
    assert utils.reformat_time('1:02:03') == '1h, 2m, and 3s'
