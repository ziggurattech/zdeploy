"""Remote client helpers for recipes."""

from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient


class SSH(SSHClient):
    """SSH helper that exposes a simple execute function."""

    def __init__(self, recipe, log, hostname, username, password, port):
        super().__init__()
        self.load_system_host_keys()
        self.set_missing_host_key_policy(AutoAddPolicy())
        self.connect(hostname=hostname, port=port, username=username, password=password)
        self.recipe = recipe
        self.log = log

    def __del__(self):
        """Ensure the SSH connection is closed."""

        self.close()

    def execute(
        self,
        *args,
        bail_on_failure=True,
        show_command=True,
        show_output=True,
        show_error=True,
    ):
        """Run ``args`` over SSH and return the exit code."""
        cmd = " ".join(args)
        if show_command:
            self.log.info("Running", cmd)
        _, stdout, _ = self.exec_command("%s 2>&1" % cmd)
        if show_output:
            for line in stdout:
                self.log.info("%s: %s" % (self.recipe, line.rstrip()))
        rc = stdout.channel.recv_exit_status()
        if rc != 0:
            if show_error:
                self.log.fail("Failed to run '%s'. Exit code: %d" % (cmd, rc))
            if bail_on_failure:
                raise Exception("failed to execute %s" % cmd)
        return rc


class SCP(SCPClient):
    """SCP helper for transferring files over SSH."""

    def __init__(self, transport):
        super().__init__(transport)

    def __del__(self):
        """Ensure the SCP connection is closed."""

        self.close()

    def upload(self, src, dest):
        """Upload ``src`` to ``dest`` on the remote host."""

        self.put(src, remote_path=dest)
