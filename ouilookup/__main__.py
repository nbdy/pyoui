from ouilookup import OUI
from argparse import ArgumentParser
from loguru import logger as log


def main():
    ap = ArgumentParser()
    ap.add_argument("-o", "--outfile", default="/tmp/oui.txt", help="oui file which will be downloaded and read.")
    ap.add_argument("-d", "--debug", action="store_true", help="enable debugging")
    ap.add_argument("-p", "--prefix", help="search by mac prefix")
    ap.add_argument("-c", "--company", help="search by company name")
    a = ap.parse_args()
    oui_entries = OUI(a.outfile, a.debug).parse()
    r = None
    if a.prefix is not None:
        r = oui_entries.lookup(a.prefix)
    elif a.company is not None:
        r = oui_entries.lookup(a.company)

    if r is None:
        log.error("could not find entry!")
    else:
        log.info(r.__dict__)


if __name__ == '__main__':
    main()
