from pathlib import Path

import pytest

from cfb_analytics.sources.cfbd.client import CfbdClient, CfbdError


def test_client_loads_api_key_from_dotenv(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("CFBD_API_KEY", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text('CFBD_API_KEY="file-secret"\n')
    with CfbdClient(env_file=env_file) as client:
        assert client._client.headers["authorization"] == "Bearer file-secret"


def test_process_environment_has_priority_over_dotenv(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("CFBD_API_KEY", "process-secret")
    env_file = tmp_path / ".env"
    env_file.write_text("CFBD_API_KEY=file-secret\n")
    with CfbdClient(env_file=env_file) as client:
        assert client._client.headers["authorization"] == "Bearer process-secret"


def test_client_reports_both_supported_key_locations(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("CFBD_API_KEY", raising=False)
    with pytest.raises(CfbdError, match="environment or .env"):
        CfbdClient(env_file=tmp_path / "missing.env")

