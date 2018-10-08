import urllib
from os.path import isfile

import progressbar

URLS = [
    "https://standards.ieee.org/develop/regauth/oui/oui.csv",
    "https://standards.ieee.org/develop/regauth/oui28/mam.csv",
    "https://standards.ieee.org/develop/regauth/oui36/oui36.csv",
    "https://standards.ieee.org/develop/regauth/cid/cid.csv",
    "https://standards.ieee.org/develop/regauth/ethertype/eth.csv",
    "https://standards.ieee.org/develop/regauth/manid/manid.csv",
    "https://standards.ieee.org/develop/regauth/bopid/opid.csv",
    "https://standards.ieee.org/develop/regauth/iab/iab.csv"
]


def _load(url, csv_file):
    if not isfile(csv_file):
        try:
            urllib.urlretrieve(url, csv_file)
        except IOError as e:
            print e.message


def dump(d="csv/"):
    bar = progressbar.ProgressBar()
    for url in bar(URLS):
        csv_file = d + url.split("/")[-1]
        _load(url, csv_file)


if __name__ == '__main__':
    dump()
