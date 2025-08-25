import json
import unittest
from unittest.mock import patch, MagicMock

from alerters.sound_alerter import SoundAlerter

class TestSoundAlerter(unittest.TestCase):
    @patch("socket.socket")
    def test_alert_sends_full_command(self, mock_socket_ctor):
        mock_sock = MagicMock()
        mock_socket_ctor.return_value = mock_sock
        mock_sock.recv.return_value = b"ACK"

        alerter = SoundAlerter()
        alerter.alert(
            level=3,
            magnitude=5.1,
            place="Somewhere",
            melody_name="ALERT_LEVEL_3",
            duration=60,
            wait=False
        )

        sent = mock_sock.sendall.call_args[0][0]
        payload = json.loads(sent.decode("utf-8"))
        assert payload["melody"] == "ALERT_LEVEL_3"
        assert payload["duration"] == 60
        assert payload["wait"] is False

        mock_sock.recv.assert_called()

if __name__ == "__main__":
    unittest.main()
