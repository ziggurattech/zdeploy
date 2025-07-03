from zdeploy.shell import execute

def test_execute_echo():
    output, rc = execute('echo hello')
    assert output.strip() == 'hello'
    assert rc == 0
