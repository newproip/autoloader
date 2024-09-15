from select import select
from signal import signal, SIGINT
from socket import socket
from socket import error as SocketError
from threading import RLock
from time import time

from newpro_autoloader.device_error import DeviceError, DeviceException

DEFAULT_TIMEOUT: float = 5.0
RECEIVE_COUNT: int = 2048

class Connection:
    """Send and receive byte arrays with message framing based on 
    a terminator byte sequence"""

    @classmethod
    def _cancel(cls, signum, frame):
        cls._abort_send = True

    def __init__(self,
                 address: list[str],
                 port: int,
                 terminator: bytearray):
        """Create a socket connection.  Does not try to connect until
        a message is sent."""

        Connection._abort_send = False
        signal(SIGINT, Connection._cancel)

        self._address = address
        self._port = port
        self._terminator = terminator

        self._address_active: str = None
        self._lock = RLock()
        self._socket: socket = None
        self._select_timeout = 0.5

    def send(self,
             msg: bytearray,
             timeout: float = DEFAULT_TIMEOUT,
    ) -> bytearray:
        with self._lock:
            if not self._is_connected:
                self._connect()

            try:
                self._socket.send(msg)
                Connection._abort_send = False

                start: float = time()
                response: bytearray = bytearray()
                while True:
                    if Connection._abort_send:
                        raise DeviceException(DeviceError.Cancelled)
                    
                    if time() - start > timeout:
                        raise DeviceException(DeviceError.Timeout)
                    
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
                        DeviceException(DeviceError.ConnectionFailed)
                    self._socket.setblocking(False)
                    self._address_active = address
                    return
                
                except Exception as ex:
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
    