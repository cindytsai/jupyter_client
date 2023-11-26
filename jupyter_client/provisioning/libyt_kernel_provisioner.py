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


class LibytKernelProvisioner(KernelProvisionerBase):  # type:ignore
    process = None  # kernel process
    pid = None  # pid of the kernel process
    pgid = None
    ip = None

    # It finds these files in directory set through environment variable LIBYT_KERNEL_INFO_DIR
    kernel_pid_filename = "libyt_kernel_pid.txt"
    kernel_connection_filename = "libyt_kernel_connection.json"

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
        import os, json
        libyt_kernel_info_dir = os.getenv("LIBYT_KERNEL_INFO_DIR")

        if libyt_kernel_info_dir is None:
            msg = "Environment variable LIBYT_KERNEL_INFO_DIR is not set."
            raise ValueError(msg)

        try:
            connection_filename = libyt_kernel_info_dir + self.kernel_connection_filename
            with open(connection_filename, "r") as f:
                connection = json.load(f)
        except FileNotFoundError:
            msg = "Unable to open '%s'" % libyt_kernel_info_dir + self.kernel_connection_filename
            raise FileNotFoundError(msg)

        # Encode key to byte string literal
        connection["key"] = connection["key"].encode("utf-8")

        # It looks like we don't need to bind to session.
        self.connection_info = connection

        # TODO: have no idea what cmd is for, but it seems jupyter-frontend is complaining.
        return await super().pre_launch(cmd="", **kwargs)

    async def launch_kernel(self, cmd: List[str], **kwargs: Any) -> KernelConnectionInfo:
        # Get LIBYT_KERNEL_INFO_DIR in environment variable
        import os
        libyt_kernel_info_dir = os.getenv("LIBYT_KERNEL_INFO_DIR")

        if libyt_kernel_info_dir is None:
            msg = "Environment variable LIBYT_KERNEL_INFO_DIR is not set."
            raise ValueError(msg)

        try:
            kernel_pid_filename = libyt_kernel_info_dir + self.kernel_pid_filename
            with open(kernel_pid_filename, "r") as f:
                pid = int(f.read())
        except FileNotFoundError:
            msg = "Unable to open '%s'" % libyt_kernel_info_dir + self.kernel_pid_filename
            raise FileNotFoundError(msg)

        pgid = None
        self.pid = pid
        self.pgid = pgid
        return self.connection_info

    async def cleanup(self, restart: bool = False) -> None:
        pass
