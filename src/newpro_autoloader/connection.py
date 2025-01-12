"""Low-level communication functions including message framing"""
from select import select
from socket import socket
from threading import RLock
from time import time

from newpro_autoloader.device_error import DeviceError, DeviceException

DEFAULT_TIMEOUT: float = 5.0
RECEIVE_COUNT: int = 2048

class Connection:
    """Send and receive byte arrays with message framing based on 
    a terminator byte sequence"""

    def __init__(self,
                 address: list[str],
                 port: int,
                 terminator: bytearray):
        """Create a socket connection.  Does not try to connect until
        a message is sent."""

        self._address = address
        self._port = port
        self._terminator = terminator

        self._address_active: str | None = None
        self._lock = RLock()
        self._socket: socket | None = None
        self._select_timeout = 0.5
        self._abort_send = False

    def cancel(self):
        """Stop a communication in progress"""
        self._abort_send = True

    def send(self,
             msg: bytearray,
             timeout: float = DEFAULT_TIMEOUT,
    ) -> bytearray:
        """Send a byte array and wait for a response"""
        with self._lock:
            if not self._is_connected:
                self._connect()

            try:
                self._socket.send(msg)
                self._abort_send = False

                start: float = time()
                response: bytearray = bytearray()
                while True:
                    if self._abort_send:
                        raise DeviceException(DeviceError.CANCELLED)

                    if time() - start > timeout:
                        raise DeviceException(DeviceError.TIMEOUT)

                    ready_sockets = select([self._socket], [], [], self._select_timeout)
                    if ready_sockets[0]:
                        response.extend(self._socket.recv(RECEIVE_COUNT))
                        if self._terminator is None:
                            return response

                        idx: int = response.find(self._terminator)
                        if idx == -1:
                            continue

                        return response[:idx + len(self._terminator)]

            except:
                self._disconnect()
                raise

    @property
    def address_active(self) -> str:
        """Address of the active connection, if any"""
        return self._address_active

    @property
    def _is_connected(self) -> bool:
        return self._socket is not None

    def _connect(self):
        ex_saved: Exception = None

        with self._lock:
            for address in self._address:
                try:
                    self._disconnect()
                    self._socket = socket()
                    ret = self._socket.connect_ex((address, self._port))
                    if ret != 0:
                        raise DeviceException(DeviceError.CONNECTION_FAILED)
                    self._socket.setblocking(False)
                    self._address_active = address
                    return

                except Exception as ex:   # pylint: disable=broad-exception-caught
                    self._socket = None
                    self._address_active = None
                    ex_saved = ex

        if ex_saved is not None:
            raise ex_saved

    def _disconnect(self):
        with self._lock:
            if self._is_connected:
                self._socket.close()
                self._socket = None
                self._address_active = None
