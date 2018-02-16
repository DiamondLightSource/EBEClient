"""A class to receive and print UDP messages."""

from socket import socket, AF_INET, SOCK_DGRAM
import logging


class EBESim(object):

    """A class to receive and respond to messages."""

    logger = logging.getLogger("EBESim")

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
        elif "?1234 GetParaLimits" in request:
            if "17" in request:
                # High voltage
                self._send(address, "!1234 GetParaLimits OK: 0;2000")
            else:
                self._send(address, "!1234 GetParaLimits OK: <LOW>;<HIGH>")
        elif "?1234 GetParaName" in request:
            if "17" in request:
                # High voltage
                self._send(address, "!1234 GetParaName OK: Voltage")
            else:
                self._send(address, "!1234 GetParaName OK: <NAME>")
        elif "?1234 GetParaValue" in request:
            if "17" in request:
                # High voltage
                self._send(address, "!1234 GetParaValue OK: 1500")
            else:
                self._send(address, "!1234 GetParaValue OK: <VALUE>")
        elif "?1234 SetParaValue" in request:
            self._send(address, "!1234 SetParaValue OK: <VALUE>")
        else:
            self._send(address, "!1234 UnknownCommand OK: None")

    def _send(self, address, message):
        self.logger.debug("Sending message: %s", message)
        self._socket.sendto(message, address)
