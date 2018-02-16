from unittest import TestCase
from mock import patch

from ebeclient import EBEClient

ebeclient_patch = "ebe.ebeclient."
socket_patch = ebeclient_patch + "socket"


class TestEBEClient(TestCase):

    @patch(socket_patch)
    def setUp(self, _):
        self.client = EBEClient("test", 1234)

    def test_send(self):
        message = "?1234 SetParaValue 5 10"
        self.client._socket.recvfrom.return_value = ("Done", 5678)
        expected_response = "Done"

        response = self.client._send(message)

        self.client._socket.sendto.assert_called_once_with(
            message, self.client._server)
        self.client._socket.recvfrom.assert_called_once_with(1024)
        self.assertEqual(expected_response, response)

    @patch(ebeclient_patch + "EBEClient._send")
    @patch(ebeclient_patch + "EBEClient._validate_response")
    def test_get(self, validate_mock, send_mock):
        expected_command = "?1234 GetParaValue 5\n"

        value = self.client.get(5)

        send_mock.assert_called_once_with(
            expected_command)
        validate_mock.assert_called_once_with(
            send_mock.return_value, expected_command)
        self.assertEqual(value, validate_mock.return_value)

    @patch(ebeclient_patch + "EBEClient._send")
    @patch(ebeclient_patch + "EBEClient._validate_response")
    def test_set(self, validate_mock, send_mock):
        expected_command = "?1234 SetParaValue 5 10\n"

        value = self.client.set(5, 10)

        send_mock.assert_called_once_with(
            expected_command)
        validate_mock.assert_called_once_with(
            send_mock.return_value, expected_command)
        self.assertIsNone(value)
