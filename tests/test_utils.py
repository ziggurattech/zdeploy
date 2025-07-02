import zdeploy.utils as utils

def test_reformat_time():
    assert utils.reformat_time('1:02:03') == '1h, 2m, and 3s'


def test_str2bool():
    assert utils.str2bool('yes') is True
    assert utils.str2bool('true') is True
    assert utils.str2bool('enable') is True
    assert utils.str2bool('no') is False
    assert utils.str2bool('maybe') is False
