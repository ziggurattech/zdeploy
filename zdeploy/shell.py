import subprocess

def execute(cmd):
    proc = subprocess.Popen('%s 2>&1' % cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True,
                            universal_newlines=True)
    std_out, _ = proc.communicate()
    rc = proc.returncode
    return std_out, rc
