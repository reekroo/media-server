import json
import logging
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from alerters.sound_alerter import SoundAlerter

@pytest.mark.asyncio
@patch("asyncio.open_unix_connection")
async def test_alert_sends_correct_command(mock_open_connection):
    mock_reader = AsyncMock()
    mock_writer = AsyncMock()
    mock_writer.write = MagicMock()
    mock_writer.close = MagicMock()

    mock_open_connection.return_value = (mock_reader, mock_writer)

    mock_logger = MagicMock(spec=logging.Logger)
    alerter = SoundAlerter(logger=mock_logger, socket_path="/tmp/test_buzzer.sock")

    await alerter.alert(
        level=3,
        magnitude=5.1,
        place="Somewhere",
        melody_name="ALERT_LEVEL_3",
        duration=60,
        wait=False
    )

    mock_open_connection.assert_awaited_with("/tmp/test_buzzer.sock")

    mock_writer.write.assert_called_once()
    sent_data_bytes = mock_writer.write.call_args[0][0]
    payload = json.loads(sent_data_bytes.decode("utf-8"))

    assert payload["melody"] == "ALERT_LEVEL_3"
    assert payload["duration"] == 60.0
    assert payload["wait"] is False