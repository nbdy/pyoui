from requests import get
from loguru import logger as log
from os.path import isfile, join
from tempfile import gettempdir
from pycountry import countries
from typing import List, Iterator


class Organization(object):
    name: str = None
    street: str = None
    district: str = None
    country: str = None

    def __init__(self, name, street=None, district=None, country=None):
        self.name = name
        self.street = street
        self.district = district
        self.country = country


class OuiEntry(object):
    prefix: str = None
    organization: Organization = None

    def __init__(self, prefix: str, organization: Organization = None):
        self.prefix = prefix
        if "-" in self.prefix:
            self.prefix = self.prefix.replace('-', ':')
        self.organization = organization


class OuiEntries(object):
    entries: list = []

    def __init__(self, infile):
        self.entries = self.parse(infile)

    @staticmethod
    def parse(filename, debug=False) -> List[OuiEntry]:
        if debug:
            log.debug("parsing entries")
        lst = []
        with open(filename) as i:
            c = -1
            t = None
            o = None
            for _ in i:
                if "(hex)" in _ and c == -1:
                    c = 0
                    t = OuiEntry(_[0:8])
                    o = Organization(_[18:].strip("\n"))
                if c == 2:
                    o.street = _.strip()
                elif c == 3:
                    o.district = _.strip()
                elif c == 4:
                    o.country = _.strip()
                    t.organization = o
                    c = 42
                if c == 42:
                    lst.append(t)
                    c = -1
                if c not in [-1, 42]:
                    c += 1
        return lst

    def by_mac(self, mac: str) -> Iterator[OuiEntry]:
        for e in self.entries:
            if mac.startswith(e.prefix):
                yield e

    def by_prefix(self, prefix: str) -> Iterator[OuiEntry]:
        for e in self.entries:
            if e.prefix == prefix:
                yield e

    def by_organization(self, name: str) -> Iterator[OuiEntry]:
        for e in self.entries:
            if name.lower() in e.organization.name.lower():
                yield e

    def by_country_name(self, name: str) -> Iterator[OuiEntry]:
        try:
            return self.by_country_code(countries.search_fuzzy(name)[0].alpha_2)
        except LookupError:
            return []

    def by_country_code(self, cc: str) -> Iterator[OuiEntry]:
        if cc is None:
            return None
        if len(cc) != 2:
            return None  # country code needs to be a length of two
        for e in self.entries:
            if e.organization.country == cc:
                yield e

    def size(self) -> int:
        return len(self.entries)


class OUI(object):
    oui_url: str = "http://standards-oui.ieee.org/oui.txt"
    outfile: str = None
    debug: bool = False

    def __init__(self, outfile=join(gettempdir(), "oui.txt"), debug=False):
        self.outfile = outfile
        self.debug = debug
        self.load()

    def load(self):
        if not isfile(self.outfile):
            if self.debug:
                log.debug("downloading {0} to {1}".format(self.oui_url, self.outfile))
            with open(self.outfile, "w") as o:
                o.write(get(self.oui_url).content.decode("utf-8"))
        else:
            if self.debug:
                log.debug("{0} already exists. not downloading.".format(self.outfile))

    def parse(self):
        if self.debug:
            log.debug("parsing {0}".format(self.outfile))
        return OuiEntries(infile=self.outfile)
