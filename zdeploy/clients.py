"""Remote client helpers for recipes."""

from paramiko import SSHClient, AutoAddPolicy, Transport
from scp import SCPClient

from zdeploy.log import Log


class SSH(SSHClient):
    """SSH helper that exposes a simple execute function."""

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        recipe: str,
        log: Log,
        hostname: str,
        username: str,
        password: str | None,
        port: int,
    ) -> None:
        """Establish an SSH connection to ``hostname``."""

        super().__init__()
        self.load_system_host_keys()
        self.set_missing_host_key_policy(AutoAddPolicy())
        self.connect(hostname=hostname, port=port, username=username, password=password)
        self.recipe = recipe
        self.log = log

    def __del__(self) -> None:
        """Ensure the SSH connection is closed."""

        self.close()

    def execute(
        self,
        *args: str,
        bail_on_failure: bool = True,
        show_command: bool = True,
        show_output: bool = True,
        show_error: bool = True,
    ) -> int:
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

    def __init__(self, transport: Transport) -> None:
        """Create an SCP client using ``transport``."""

        super().__init__(transport)

    def __del__(self) -> None:
        """Ensure the SCP connection is closed."""

        self.close()

    def upload(self, src: str, dest: str) -> None:
        """Upload ``src`` to ``dest`` on the remote host."""

        self.put(src, remote_path=dest)
