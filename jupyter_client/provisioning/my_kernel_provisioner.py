import asyncio
import json
import os
import socket
import signal
import sys
from subprocess import PIPE
from typing import Any, Dict, List, Optional

from jupyter_client import KernelConnectionInfo

from .provisioner_base import KernelProvisionerBase


class MyKernelProvisioner(KernelProvisionerBase):  # type:ignore
    process = None  # kernel process
    pid = None  # pid of the kernel process
    pgid = None
    ip = None

    @property
    def has_process(self) -> bool:
        """
        If this provisioner is currently managing a process.
        """
        # TODO: We manually manage kernel now
        return True

    async def poll(self) -> Optional[int]:
        """
        Check if kernel process is still running.
        """
        # TODO: We manually manage kernel now, so always report process is alive, which is returning None.
        return None

    async def wait(self) -> Optional[int]:
        # TODO: Not sure if I need this, closing stdout/stderr/stdin
        # ret = 0
        # if self.process:
        #     while await self.poll() is None:
        #         await asyncio.sleep(0.1)
        #
        #     # Process is no longer alive, wait and clear
        #     ret = self.process.wait()
        #     # Make sure all the fds get closed.
        #     for attr in ["stdout", "stderr", "stdin"]:
        #         fid = getattr(self.process, attr)
        #         if fid:
        #             fid.close()
        #     self.process = None
        # return ret
        pass

    async def send_signal(self, signum: int) -> None:
        # TODO: Not sure if I need this, probably do, but not now.
        # if self.process:
        #     if signum == signal.SIGINT and sys.platform == "win32":
        #         from jupyter_client.win_interrupt import send_interrupt
        #
        #         send_interrupt(self.process.win32_interrupt_event)
        #         return
        #
        #     # Prefer process-group over process
        #     if self.pgid and hasattr(os, "killpg"):
        #         try:
        #             os.killpg(self.pgid, signum)
        #             return
        #         except OSError:
        #             pass
        #     return self.process.send_signal(signum)
        pass

    async def kill(self, restart: bool = False) -> None:
        # TODO: We manually manage kernel now
        # if self.process:
        #     self.process.kill()
        pass

    async def terminate(self, restart: bool = False) -> None:
        # TODO: We manually manage kernel now
        pass

    async def pre_launch(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Connecting to hard-coded port for now
        """
        connection_json = {
            "control_port": 50160,
            "shell_port": 57503,
            "transport": "tcp",
            "signature_scheme": "hmac-sha256",
            "stdin_port": 52597,
            "hb_port": 42540,
            "ip": "127.0.0.1",
            "iopub_port": 40885,
            "key": "a0436f6c-1916-498b-8eb9-e81ab9368e84"
        }

        # TODO: connect to port using the above
        port_name_list = ["shell_port", "iopub_port", "stdin_port", "hb_port", "control_port"]
        for port_name in port_name_list:
            tmp_sock = socket.socket()
            tmp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, b"\0" * 8)  # Don't know what is this line for
            tmp_sock.bind((connection_json["ip"], connection_json[port_name]))
            assert tmp_sock.getsockname()[1] == connection_json[port_name], "Port not bind to what we specified!!\n"
            tmp_sock.close()

        # It looks like we don't need to bind to session.
        self.connection_info = connection_json

        return await super().pre_launch(**kwargs)

    async def launch_kernel(self, cmd: List[str], **kwargs: Any) -> KernelConnectionInfo:
        # We launch kernel manually, but we need to get its pid through reading files
        kernel_pid_filename = "/home/cindytsai/Packages/xeus-zmq-1.1.0/example/build/kernel_pid.txt"
        with open(kernel_pid_filename, "r") as f:
            pid = int(f.read())
        pgid = None
        self.pid = pid
        self.pgid = pgid
        return self.connection_info

    async def cleanup(self, restart: bool = False) -> None:
        pass
