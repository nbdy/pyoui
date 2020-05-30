from requests import get
from loguru import logger as log
from os.path import isfile


class OuiEntries(object):
    entries = []

    def __init__(self, infile):
        self.entries = self.parse(infile)

    @staticmethod
    def parse(filename):
        lst = []
        with open(filename) as i:
            for _ in i:
                if "(hex)" in _:
                    lst.append(OuiEntry(address=_[0:8], company=_[18:]))
        return lst

    def by_mac(self, mac: str):
        for e in self.entries:
            if mac.startswith(e.address):
                return SearchResult(mac, e)
        return None

    def by_prefix(self, prefix):
        for e in self.entries:
            if prefix.startswith(e.address):
                return SearchResult(prefix, e)
        return None

    def by_company(self, name):
        for e in self.entries:
            if name in e.company:
                return SearchResult(e.address, e)
        return None

    def lookup_multiple(self, addresses):
        r = []
        for e in self.entries:
            for address in addresses:
                if address.startswith(e.address):
                    r.append(SearchResult(address=address, entry=e))
        return r


class SearchResult(object):
    address = None
    entry = None

    def __init__(self, address, entry):
        self.address = address
        self.entry = entry


class OuiEntry(object):
    address = None
    company = None

    def __init__(self, address, company):
        self.address = address
        if "-" in self.address:
            self.address = self.address.replace('-', ':')
        self.company = company


class OUI(object):
    oui_url = "http://standards-oui.ieee.org/oui.txt"
    outfile = None
    debug = False

    def __init__(self, outfile="/tmp/oui.txt", debug=False):
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
