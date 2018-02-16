from unittest import TestCase
from mock import patch

from ebeclient import EBEClient

ebeclient_patch = "ebe.ebeclient."
socket_patch = ebeclient_patch + "socket"


class TestEBEClient(TestCase):

    @patch(socket_patch)
    def setUp(self, _):
        self.client = EBEClient("test", 1234, debug=True)

    def test_send(self):
        message = "?1234 SetParaValue 5 10"
        self.client._socket.recvfrom.return_value = ("Done", 5678)
        expected_response = "Done"

        response = self.client._send(message)

        self.client._socket.sendto.assert_called_once_with(
            message, self.client._server)
        self.client._socket.recvfrom.assert_called_once_with(1024)
        self.assertEqual(expected_response, response)

    @patch(ebeclient_patch + "EBEClient.get_param_name",
           return_value="Voltage")
    @patch(ebeclient_patch + "EBEClient._send")
    @patch(ebeclient_patch + "EBEClient._validate_response")
    def test_get(self, validate_mock, send_mock, get_name_mock):
        expected_command = "?1234 GetParaValue 17\n"
        validate_mock.return_value = 10

        value = self.client.get(17)

        send_mock.assert_called_once_with(
            expected_command)
        validate_mock.assert_called_once_with(
            send_mock.return_value, "GetParaValue")
        self.assertEqual(value, validate_mock.return_value)

    @patch(ebeclient_patch + "EBEClient._send")
    @patch(ebeclient_patch + "EBEClient._validate_response")
    def test_get_name(self, validate_mock, send_mock):
        expected_command = "?1234 GetParaName 17\n"
        validate_mock.return_value = "Voltage"

        value = self.client.get_param_name(17)

        send_mock.assert_called_once_with(
            expected_command)
        validate_mock.assert_called_once_with(
            send_mock.return_value, "GetParaName")
        self.assertEqual(value, validate_mock.return_value)

    @patch(ebeclient_patch + "EBEClient._send")
    @patch(ebeclient_patch + "EBEClient._validate_response")
    def test_get_limits(self, validate_mock, send_mock):
        expected_command = "?1234 GetParaLimits 17\n"
        validate_mock.return_value = "0;2000"

        value = self.client.get_param_limits(17)

        send_mock.assert_called_once_with(
            expected_command)
        validate_mock.assert_called_once_with(
            send_mock.return_value, "GetParaLimits")
        self.assertEqual(value, (0, 2000))

    @patch(ebeclient_patch + "EBEClient.get_param_limits",
           return_value=(0, 2000))
    @patch(ebeclient_patch + "EBEClient.get_param_name",
           return_value="Voltage")
    @patch(ebeclient_patch + "EBEClient._send")
    @patch(ebeclient_patch + "EBEClient._validate_response")
    def test_set(self, validate_mock, send_mock, _, _2):
        expected_command = "?1234 SetParaValue 17 1500\n"

        value = self.client.set(17, 1500)

        send_mock.assert_called_once_with(
            expected_command)
        validate_mock.assert_called_once_with(
            send_mock.return_value, "SetParaValue")
        self.assertIsNone(value)

    @patch(ebeclient_patch + "EBEClient._send")
    def test_set_remote_mode(self, send_mock):
        expected_command = "?1234 SetRemoteMode 1\n"

        value = self.client.set_remote_mode()

        send_mock.assert_called_once_with(
            expected_command)
        self.assertIsNone(value)
