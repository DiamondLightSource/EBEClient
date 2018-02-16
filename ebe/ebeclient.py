"""A class to control an EBE-4."""

import re
from socket import socket, AF_INET, SOCK_DGRAM, timeout
import logging


class EBEClient(object):

    """A class to control an EBE-4."""

    TIMEOUT = 3
    COMMAND_TEMPLATE = "?1234 {command}\n"
    GET_REQUEST = COMMAND_TEMPLATE.format(command="GetParaValue {param}")
    SET_REQUEST = COMMAND_TEMPLATE.format(command="{method} {value}")
    SET_PARAM_METHOD = "SetParaValue {param}"
    # !1234|Param|OK:|Value|\n -- param and val need whitespace stripped
    RESPONSE_REGEX = re.compile(r"!1234(?P<command>.+)(?P<status>.+)\n")
    OK_STATUS_REGEX = re.compile(r"OK:(?P<value>.+)")
    ERROR_STATUS_REGEX = re.compile(r"Error:(?P<error>.+)")

    def __init__(self, ip, port, debug=False):
        """
        Args:
            ip(str): IP address to send and receive commands on
            port(int): Port ...
            debug(bool): Whether to enable debug logging

        """
        self.logger = logging.getLogger(self.__class__.__name__)
        if debug:
            level = 10  # Debug
            log_format = "%(asctime)s - %(name)s.%(funcName)s - " \
                         "%(levelname)s - %(message)s"
        else:
            level = 20  # Info
            log_format = "%(message)s"
        logging.basicConfig(level=level, format=log_format)

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
        command = self.GET_REQUEST.format(param=param)
        response = self._send(command)
        if response is not None:
            value = self._validate_response(response, command)
            if value is not None:
                self.logger.debug("Param %d = %s", param, value)
                return value

        raise IOError("Get failed on param %s" % param)

    def set(self, param, value):
        self.logger.debug("Sending SET request: %d = %s", param, str(value))
        command = self.SET_REQUEST.format(
            method=self.SET_PARAM_METHOD.format(param=param), value=value)
        response = self._send(command)
        if response is not None:
            if self._validate_response(response, command):
                self.logger.info("Param %s successfully set to %s",
                                 param, value)
                return
            else:
                self.logger.error("Value not set to requested value")

        raise IOError("Set failed on param %s" % param)

    def _validate_response(self, response, requested_command):
        match = re.match(self.RESPONSE_REGEX, response)
        if match:
            command, status = match.groups()
            command = command.strip(" ")
            status = status.strip(" ")
            if command != requested_command:
                self.logger.error("Failed to match response to request")
                return
        else:
            self.logger.error("Failed to parse response: %s", response)
            return

        match = re.match(self.OK_STATUS_REGEX, status)
        if match:
            value = match.groups()[0].strip(" ")
            return value

        match = re.match(self.ERROR_STATUS_REGEX, status)
        if match:
            error = match.groups()[0].strip(" ")
            self.logger.error("Got error in response: %s", error)
            return
