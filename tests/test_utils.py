import zdeploy.utils as utils
import pytest

def test_reformat_time():
    assert utils.reformat_time('1:02:03') == '1h, 2m, and 3s'


def test_str2bool():
    assert utils.str2bool('yes') is True
    assert utils.str2bool('no') is False
    with pytest.raises(ValueError):
        utils.str2bool('maybe')
