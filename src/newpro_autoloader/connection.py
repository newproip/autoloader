from socket import socket
from threading import RLock

DEFAULT_TIMEOUT: float = 5.0
RECEIVE_COUNT: int = 2048

class Connection:

    def __init__(self,
                 address: list[str],
                 port: int,
                 terminator: bytearray):
        """Create a socket connection.  Does not try to connect until
        a message is sent."""

        self._address = address
        self._port = port
        self._terminator = terminator

        self._address_active: str = None
        self._lock = RLock()
        self._socket: socket = None

    def send(self,
             msg: bytearray,
             timeout: float = DEFAULT_TIMEOUT,
    ) -> bytearray:
        """Send a message and receive the response"""

        with self._lock:
            if not self._is_connected:
                self._connect()

            try:
                self._socket.settimeout(timeout)
                self._socket.send(msg)

                response: bytearray = bytearray()
                while True:
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
        ex: Exception = None

        with self._lock:
            for address in self._address:
                try:
                    self._disconnect()
                    self._socket = socket()
                    self._socket.settimeout(DEFAULT_TIMEOUT)
                    self._socket.connect((address, self._port))
                    self._address_active = address
                    break
                
                except ex:
                    self._socket = None
                    self._address_active = None

        if ex is not None:
            raise ex
    
    def _disconnect(self):
        with self._lock:
            if self._is_connected:
                self._socket.close()
                self._socket = None
                self._address_active = None
    