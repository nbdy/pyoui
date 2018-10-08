import urllib2
from os.path import isfile


class OuiEntries(object):
    infile = None
    entries = []

    def __init__(self, **kwargs):
        if "infile" in kwargs.keys():
            self.infile = kwargs.get("infile")
        else:
            self.infile = "oui.txt"
        self.entries = self.parse(self.infile)

    @staticmethod
    def parse(filename):
        l = []
        with open(filename) as i:
            for _ in i:
                if "(hex)" in _:
                    l.append(OuiEntry(address=_[0:8], company=_[18:]))
        return l

    def lookup(self, address):
        for e in self.entries:
            if address.startswith(e.address):
                return SearchResult(address=address, entry=e)
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

    def __init__(self, **kwargs):
        if "address" in kwargs.keys():
            self.address = kwargs.get("address")
        if "entry" in kwargs.keys():
            self.entry = kwargs.get("entry")


class OuiEntry(object):
    address = None
    company = None

    def __init__(self, **kwargs):
        if "address" in kwargs.keys():
            self.address = kwargs.get("address")
            if "-" in self.address:
                self.address = self.address.replace('-', ':')
        if "company" in kwargs.keys():
            self.company = kwargs.get("company")


class OUI(object):
    oui_url = "http://standards-oui.ieee.org/oui.txt"
    outfile = None
    entries = None

    def __init__(self, **kwargs):
        if "oui_url" in kwargs.keys():
            self.oui_url = kwargs.get("oui_url")
        if "outfile" in kwargs.keys():
            self.outfile = kwargs.get("outfile")
        else:
            self.outfile = "oui.txt"
        if "entries" in kwargs.keys():
            self.entries = kwargs.get("entries")

    def load(self):
        if not isfile(self.outfile):
            print "downloading", self.oui_url, "to", self.outfile
            with open(self.outfile, "w") as o:
                o.write(urllib2.urlopen(self.oui_url).read())
        else:
            print "not downloading", self.oui_url
            print self.outfile, "already exists"

    def parse(self):
        print "parsing", self.outfile
        self.entries = OuiEntries(infile=self.outfile)


if __name__ == '__main__':
    o = OUI()
    o.load()
    o.parse()
