from unittest.mock import patch, MagicMock
from ..src.get_imms_handler import get_imms_handler
import json


@patch('lambda_code.src.get_imms_handler.EventTable')
def test_get_imms_handler_happy_path(mock_event_table):
    # Arrange
    mock_get_event_by_id = MagicMock()
    mock_get_event_by_id.return_value = "Mocked event data"
    mock_event_table.return_value.get_event_by_id = mock_get_event_by_id
    formatted_event = { "id": "sampleid" }

    #Act
    result = get_imms_handler(formatted_event, None)

    # Assert
    mock_event_table.return_value.get_event_by_id.assert_called_once_with(formatted_event["id"])
    assert result['statusCode'] == 200
    assert json.loads(result['body']) == {"message": "Mocked event data"}


def test_get_imms_handler_sad_path():
    # Arrange
    unformatted_event = {"id": "unexpected_id"}

    # Act
    result = get_imms_handler(unformatted_event, None)

    # Assert
    assert result['statusCode'] == 400
    assert result['body'] == 'ID is not formatted correctly or is missing'
