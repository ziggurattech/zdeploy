"""Remote client helpers for recipes."""

from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient


class SSH(SSHClient):
    """SSH helper that exposes a simple execute function."""

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, recipe, log, hostname, username, password, port):
        """Establish an SSH connection to ``hostname``."""

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
        _, stdout, _ = self.exec_command(f"{cmd} 2>&1")
        if show_output:
            for line in stdout:
                self.log.info(f"{self.recipe}: {line.rstrip()}")
        rc = stdout.channel.recv_exit_status()
        if rc != 0:
            if show_error:
                self.log.fail(f"Failed to run '{cmd}'. Exit code: {rc}")
            if bail_on_failure:
                raise RuntimeError(f"failed to execute {cmd}")
        return rc


class SCP(SCPClient):
    """SCP helper for transferring files over SSH."""

    def __init__(self, transport):
        """Create an SCP client using ``transport``."""

        super().__init__(transport)

    def __del__(self):
        """Ensure the SCP connection is closed."""

        self.close()

    def upload(self, src, dest):
        """Upload ``src`` to ``dest`` on the remote host."""

        self.put(src, remote_path=dest)
