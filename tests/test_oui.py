import os
import shutil
import tempfile
import unittest

from pyoui import OuiEntries


SAMPLE_CONTENT = "\n".join([
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
])


class TestOui(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp()
        cls.filepath = os.path.join(cls.tmpdir, "oui.txt")
        with open(cls.filepath, "w", encoding="utf-8") as f:
            f.write(SAMPLE_CONTENT)
        cls.entries = OuiEntries(infile=cls.filepath)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_has_entries(self):
        self.assertEqual(self.entries.size(), 4)

    def test_by_org(self):
        e = next(self.entries.by_organization("national security"))
        self.assertEqual(e.organization.street, "9800 SAVAGE ROAD")

    def test_by_prefix(self):
        e = next(self.entries.by_prefix("00:22:72"))
        self.assertEqual(e.organization.name, "American Micro-Fuel Device Corp.")

    def test_by_mac(self):
        m = "BC:23:92:42:42:42"
        e = next(self.entries.by_mac(m))
        self.assertIn(e.prefix, m)
        self.assertEqual(e.organization.name, "BYD Precision Manufacture Company Ltd.")

    def test_by_country_code(self):
        self.assertGreater(len(list(self.entries.by_country_code("US"))), 0)
        self.assertGreater(len(list(self.entries.by_country_code("DE"))), 0)
        self.assertEqual(len(list(self.entries.by_country_code("XX"))), 0)

    def test_by_country_name(self):
        self.assertGreater(len(list(self.entries.by_country_name("United States"))), 0)
        self.assertGreater(len(list(self.entries.by_country_name("Germany"))), 0)
        self.assertEqual(len(list(self.entries.by_country_name("XXX"))), 0)


if __name__ == "__main__":
    unittest.main()
