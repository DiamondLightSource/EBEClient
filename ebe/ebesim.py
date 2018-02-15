"""A class to receive and print UDP messages."""

from socket import socket, AF_INET, SOCK_DGRAM, SHUT_RDWR
import logging


class EBESim(object):

    """A class to receive and respond to messages."""

    logger = logging.getLogger("UDPListener")

    def __init__(self, ip, port):
        """
        Args:
            ip(str): IP address to listen on
            port(int): Port ...

        """
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(10)

        self._server = (ip, port)

        self._socket = socket(AF_INET,     # Internet
                              SOCK_DGRAM)  # UDP
        self._socket.bind(self._server)

    def __del__(self):
        self._socket.close()
        self._socket.shutdown(SHUT_RDWR)

    def recv(self):
        while True:
            self.logger.debug("Listening on %s:%d", *self._server)
            self.logger.debug("Listening for messages...")

            data, address = self._socket.recvfrom(1024)
            if data:
                self.logger.debug("Received %s bytes from %s",
                                  len(data), address)
                self.logger.debug("Request: %s", data)
                self._respond(address, data)

    def _respond(self, address, request):
        if "?1234 GetDeviceName" in request:
            self._send(address, "!1234 GetDeviceName OK: EBE-4")
        elif "?1234 GetParaValue" in request:
            self._send(address, "!1234 GetParaValue <PARAM> OK: <VALUE>")
        elif "?1234 SetParaValue" in request:
            self._send(address, "!1234 SetParaValue <PARAM> OK: <VALUE>")
        else:
            self._send(address, "!1234 UnknownParam OK: None")

    def _send(self, address, message):
        self.logger.debug("Sending message: %s", message)
        self._socket.sendto(message, address)
