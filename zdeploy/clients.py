from paramiko import SSHClient, AutoAddPolicy

class SSH(SSHClient):
    def __init__(self, recipe_name, log):
        SSHClient.__init__(self)
        self.load_system_host_keys()
        self.set_missing_host_key_policy(AutoAddPolicy())
        self.recipe_name = recipe_name
        self.log = log
    def execute(self, *args, bail_on_failure=True, show_command=True, show_output=True, show_error=True):
        cmd = ' '.join(args)
        if show_command:
            self.log.info('Running', cmd)
        _, stdout, _ = self.exec_command('%s 2>&1' % cmd)
        if show_output:
            for line in stdout:
                self.log.info('%s: %s' % (self.recipe_name, line.rstrip()))
        rc = stdout.channel.recv_exit_status()
        if rc is not 0:
            if show_error:
                self.log.fail("Failed to run '%s'. Exit code: %d" % (cmd, rc))
            if bail_on_failure:
                raise Exception('%s failed to run' % cmd)
        return rc