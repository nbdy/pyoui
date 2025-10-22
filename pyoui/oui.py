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
        # normalize prefix once
        p = prefix.replace('-', ':').upper() if prefix else prefix
        self.prefix = p
        self.organization = organization


class OuiEntries(object):
    def __init__(self, infile):
        self.entries: list[OuiEntry] = self.parse(infile)

    @staticmethod
    def parse(filename, debug=False) -> List[OuiEntry]:
        if debug:
            log.debug("parsing entries")
        lst: List[OuiEntry] = []
        with open(filename, encoding="utf-8") as i:
            c = -1
            t = None
            o = None
            for _ in i:
                line = _.rstrip("\n")
                if "(hex)" in line and c == -1:
                    c = 0
                    # prefix is always first 8 chars; organization follows '(hex)'
                    t = OuiEntry(line[0:8])
                    org_name = line.split("(hex)", 1)[1].strip()
                    o = Organization(org_name)
                if c == 2:
                    o.street = line.strip()
                elif c == 3:
                    o.district = line.strip()
                elif c == 4:
                    o.country = line.strip()
                    t.organization = o
                    c = 42
                if c == 42:
                    lst.append(t)
                    c = -1
                if c not in [-1, 42]:
                    c += 1
        return lst

    def by_mac(self, mac: str) -> Iterator[OuiEntry]:
        if mac is None:
            return
        n_mac = mac.replace('-', ':').upper()
        for e in self.entries:
            if n_mac.startswith(e.prefix):
                yield e

    def by_prefix(self, prefix: str) -> Iterator[OuiEntry]:
        if prefix is None:
            return
        n_prefix = prefix.replace('-', ':').upper()
        for e in self.entries:
            if e.prefix == n_prefix:
                yield e

    def by_organization(self, name: str) -> Iterator[OuiEntry]:
        if not name:
            return
        low = name.lower()
        for e in self.entries:
            if e.organization and e.organization.name and low in e.organization.name.lower():
                yield e

    def by_country_name(self, name: str) -> Iterator[OuiEntry]:
        try:
            return self.by_country_code(countries.search_fuzzy(name)[0].alpha_2)
        except LookupError:
            # empty iterator for unknown country names
            return iter(())

    def by_country_code(self, cc: str) -> Iterator[OuiEntry]:
        if not cc or len(cc) != 2:
            return
        ncc = cc.upper()
        for e in self.entries:
            if e.organization and e.organization.country == ncc:
                yield e

    def size(self) -> int:
        return len(self.entries)


class OUI(object):
    oui_url: str = "https://standards-oui.ieee.org/oui.txt"
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
            try:
                r = get(self.oui_url, timeout=30)
                r.raise_for_status()
                with open(self.outfile, "w", encoding="utf-8") as o:
                    o.write(r.content.decode("utf-8"))
            except Exception as ex:
                log.error(f"failed to download OUI list: {ex}")
                raise
        else:
            if self.debug:
                log.debug("{0} already exists. not downloading.".format(self.outfile))

    def parse(self):
        if self.debug:
            log.debug("parsing {0}".format(self.outfile))
        return OuiEntries(infile=self.outfile)
