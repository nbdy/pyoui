from pyoui import OUI

entries = OUI(debug=True).parse()


def test_has_entries():
    assert entries.size() > 0


def test_by_org():
    e = next(entries.by_organization("national security"))
    assert e.organization.street == "9800 SAVAGE ROAD"


def test_by_prefix():
    e = next(entries.by_prefix("00:22:72"))
    assert e.organization.name == "American Micro-Fuel Device Corp."


def test_by_mac():
    m = "BC:23:92:42:42:42"
    e = next(entries.by_mac(m))
    assert e.prefix in m
    assert e.organization.name == "BYD Precision Manufacture Company Ltd."


def test_by_country_code():
    assert len(list(entries.by_country_code("US"))) > 0
    assert len(list(entries.by_country_code("DE"))) > 0
    assert len(list(entries.by_country_code("XX"))) == 0


def test_by_country_name():
    assert len(list(entries.by_country_name("United States"))) > 0
    assert len(list(entries.by_country_name("Germany"))) > 0
    assert len(list(entries.by_country_name("XXX"))) == 0

