import json
import unittest
import logging
from unittest.mock import patch, MagicMock

from alerters.sound_alerter import SoundAlerter

class TestSoundAlerter(unittest.TestCase):
    
    @patch("socket.socket")
    def test_alert_sends_correct_command(self, mock_socket_class):
        mock_socket_instance = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket_instance

        mock_logger = MagicMock(spec=logging.Logger)
        alerter = SoundAlerter(logger=mock_logger, socket_path="/tmp/test_buzzer.sock")

        alerter.alert(
            level=3,
            magnitude=5.1,
            place="Somewhere",
            melody_name="ALERT_LEVEL_3",
            duration=60,
            wait=False
        )

        mock_socket_instance.connect.assert_called_with("/tmp/test_buzzer.sock")

        mock_socket_instance.sendall.assert_called_once()
        sent_data_bytes = mock_socket_instance.sendall.call_args[0][0]
        payload = json.loads(sent_data_bytes.decode("utf-8"))

        self.assertEqual(payload["melody"], "ALERT_LEVEL_3")
        self.assertEqual(payload["duration"], 60.0)
        self.assertIs(payload["wait"], False)