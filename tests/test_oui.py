"""Tests for the pyoui package."""

from unittest.mock import MagicMock, patch

import pytest
from requests import RequestException

from pyoui import OUI, OuiEntries

SAMPLE_CONTENT = "\n".join(
    [
        # 00:22:72 -> American Micro-Fuel Device Corp. (US)
        "00-22-72   (hex)   American Micro-Fuel Device Corp.",
        "",
        "123 Main St",
        "Anytown, CA 90210",
        "US",
        # BC:23:92 -> BYD Precision Manufacture Company Ltd. (CN)
        "BC-23-92   (hex)   BYD Precision Manufacture Company Ltd.",
        "",
        "Building 1",
        "Shenzhen, Guangdong 518000",
        "CN",
        # AA:BB:CC -> National Security Agency (US)
        "AA-BB-CC   (hex)   National Security Agency",
        "",
        "9800 SAVAGE ROAD",
        "Fort Meade, MD 20755",
        "US",
        # DE:AD:BE -> Deutsche Beispiel GmbH (DE)
        "DE-AD-BE   (hex)   Deutsche Beispiel GmbH",
        "",
        "Musterstraße 1",
        "12345 Musterstadt",
        "DE",
    ]
)


@pytest.fixture
def temp_oui_file(tmp_path):
    """Create a temporary OUI file for testing."""
    d = tmp_path / "data"
    d.mkdir()
    f = d / "oui.txt"
    f.write_text(SAMPLE_CONTENT, encoding="utf-8")
    return str(f)


@pytest.fixture
def entries(temp_oui_file):
    """Provide a OuiEntries instance for testing."""
    return OuiEntries(infile=temp_oui_file)


def test_has_entries(entries):
    """Check if the number of entries is correct."""
    assert entries.size() == 4


def test_by_org(entries):
    """Check searching by organization name."""
    e = next(entries.by_organization("national security"))
    assert e.organization.street == "9800 SAVAGE ROAD"


def test_by_prefix(entries):
    """Check searching by MAC prefix."""
    e = next(entries.by_prefix("00:22:72"))
    assert e.organization.name == "American Micro-Fuel Device Corp."


def test_by_mac(entries):
    """Check searching by MAC address."""
    m = "BC:23:92:42:42:42"
    e = next(entries.by_mac(m))
    assert e.prefix in m
    assert e.organization.name == "BYD Precision Manufacture Company Ltd."


def test_by_country_code(entries):
    """Check searching by country code."""
    assert len(list(entries.by_country_code("US"))) > 0
    assert len(list(entries.by_country_code("DE"))) > 0
    assert len(list(entries.by_country_code("XX"))) == 0


def test_by_country_name(entries):
    """Check searching by country name."""
    assert len(list(entries.by_country_name("United States"))) > 0
    assert len(list(entries.by_country_name("Germany"))) > 0
    assert len(list(entries.by_country_name("XXX"))) == 0


def test_oui_load_mocked(tmp_path):
    """Check OUI loading with mocked network."""
    outfile = tmp_path / "downloaded_oui.txt"
    with patch("pyoui.oui.get") as mock_get:
        mock_response = MagicMock()
        mock_response.content = SAMPLE_CONTENT.encode("utf-8")
        mock_response.status_code = 200
        mock_response.headers = {"content-length": str(len(SAMPLE_CONTENT))}
        mock_response.iter_content.return_value = [SAMPLE_CONTENT.encode("utf-8")]
        mock_get.return_value = mock_response

        OUI(outfile=str(outfile))
        assert outfile.exists()
        assert outfile.read_text(encoding="utf-8") == SAMPLE_CONTENT
        mock_get.assert_called_once()


def test_empty_file(tmp_path):
    """Check parsing an empty file."""
    f = tmp_path / "empty.txt"
    f.write_text("", encoding="utf-8")
    entries = OuiEntries(infile=str(f))
    assert entries.size() == 0


def test_malformed_file(tmp_path):
    """Check parsing a malformed file."""
    f = tmp_path / "malformed.txt"
    f.write_text("this is not a valid OUI file", encoding="utf-8")
    entries = OuiEntries(infile=str(f))
    assert entries.size() == 0


def test_non_existent_file():
    """Check behavior when file does not exist."""
    with pytest.raises(FileNotFoundError):
        OuiEntries(infile="non_existent.txt")


def test_network_failure(tmp_path):
    """Check behavior during network failure."""
    outfile = tmp_path / "fail.txt"
    with patch("pyoui.oui.get") as mock_get:
        mock_get.side_effect = RequestException("Timeout")
        with pytest.raises(RequestException):
            OUI(outfile=str(outfile))


def test_cli_json(temp_oui_file, capsys):
    """Check CLI JSON output."""
    import json
    import sys

    from pyoui.__main__ import main

    with patch.object(sys, "argv", ["pyoui", "-o", temp_oui_file, "-p", "00:22:72", "-f", "json"]):
        main()
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data) == 1
    assert data[0]["prefix"] == "00:22:72"
    assert data[0]["organization"]["name"] == "American Micro-Fuel Device Corp."


def test_invalid_mac(entries):
    """Check behavior with invalid MAC address."""
    with patch("pyoui.oui.log.warning") as mock_log:
        list(entries.by_mac("invalid"))
        mock_log.assert_called_with("Invalid MAC address: invalid")


def test_invalid_prefix(entries):
    """Check behavior with invalid MAC prefix."""
    with patch("pyoui.oui.log.warning") as mock_log:
        list(entries.by_prefix("inv"))
        mock_log.assert_called_with("Invalid MAC prefix: inv")
