"""A class to control an EBE-4."""

import re
from socket import socket, AF_INET, SOCK_DGRAM, timeout
import logging


class EBEClient(object):

    """A class to control an EBE-4."""

    TIMEOUT = 3
    COMMAND_TEMPLATE = "?1234 {command}\n"
    GET_TEMPLATE = COMMAND_TEMPLATE.format(
        command="GetParaValue {param}")
    SET_TEMPLATE = COMMAND_TEMPLATE.format(
        command="SetParaValue {param} {value}")
    # !1234|Param|OK:|Value|\n -- param and val need whitespace stripped
    RESPONSE_REGEX = re.compile(
        r"!1234(?P<param>.+)OK:(?P<value>.+)\n")

    logger = logging.getLogger("EBEClient")

    def __init__(self, ip, port):
        """
        Args:
            ip(str): IP address to send and receive commands on
            port(int): Port ...

        """
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(10)

        self._server = (ip, port)

        self._socket = socket(AF_INET,     # Internet
                              SOCK_DGRAM)  # UDP
        self._socket.settimeout(self.TIMEOUT)
        self._socket.connect(self._server)

    def __del__(self):
        self._socket.close()

    def get_device_name(self):
        self._send(self.COMMAND_TEMPLATE.format(command="GetDeviceName"))

    def _send(self, message):
        self.logger.debug("Sending message: %s", message)

        self._socket.sendto(message, self._server)
        self.logger.debug("Waiting for response...")

        try:
            data, address = self._socket.recvfrom(1024)
            if data:
                self.logger.debug("Received %s bytes from %s",
                                  len(data), address)
                self.logger.debug("Response: %s", data)
                return data
            else:
                self.logger.error("Received empty response")
        except timeout:
            self.logger.error("Receive loop timed out")

    def get(self, param):
        self.logger.debug("Sending GET request for: %d", param)
        response = self._send(self.GET_TEMPLATE.format(param=param))
        if response is not None:
            value = self._validate_response(response, param)
            if value is not None:
                return value

        raise IOError("Get failed on param %s" % param)

    def set(self, param, value):
        self.logger.debug("Sending SET request: %d = %s", param, str(value))
        response = self._send(self.SET_TEMPLATE.format(param=param,
                                                       value=value))
        if response is not None:
            new_value = self._validate_response(response, param)
            if new_value == value:
                self.logger.debug("Param %s successfully set to %s",
                                  param, value)
                return new_value
            else:
                self.logger.error(
                    "Value not set to request value: %s, Returned value: %s",
                    value, new_value)

        raise IOError("Set failed on param %s" % param)

    def _validate_response(self, response, expected_param):
        match = re.match(self.RESPONSE_REGEX, response)
        if match:
            param, value = match.groups()
            param = param.strip(" ")
            value = value.strip(" ")
            if param == expected_param:
                return value
            else:
                self.logger.error("Failed to match response to request")
