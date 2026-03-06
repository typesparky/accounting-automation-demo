import pytest
from src.infrastructure.outlook_connector import OutlookConnector

def test_outlook_connector_auth():
    connector = OutlookConnector(client_id="test", client_secret="test")
    assert connector.authenticate() is True
    assert connector.authenticated is True

def test_outlook_connector_fetch_emails():
    connector = OutlookConnector()
    connector.authenticate()
    emails = connector.fetch_emails()
    assert len(emails) > 0
    assert "id" in emails[0]
    assert "attachments" in emails[0]

def test_outlook_connector_download():
    connector = OutlookConnector()
    path = "/tmp/test_attachment.txt"
    result = connector.download_attachment("msg1", "att1", path)
    assert result == path
    import os
    assert os.path.exists(path)
    os.remove(path)
