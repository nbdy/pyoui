from pyoui import OUI
from argparse import ArgumentParser
from loguru import logger as log


def main():
    ap = ArgumentParser()
    ap.add_argument("-o", "--outfile", default="/tmp/oui.txt", help="oui file which will be downloaded and read.")
    ap.add_argument("-d", "--debug", action="store_true", help="enable debugging")
    ap.add_argument("-p", "--prefix", help="search by mac prefix")
    ap.add_argument("-org", "--organization", help="search by organization name")
    ap.add_argument("-cc", "--country-code", help="search by country code")
    ap.add_argument("-cn", "--country-name", help="search by country name")
    a = ap.parse_args()
    oui_entries = OUI(a.outfile, a.debug).parse()
    r = None
    if a.prefix is not None:
        r = oui_entries.by_prefix(a.prefix)
    elif a.organization is not None:
        r = oui_entries.by_company(a.organization)
    elif a.country_code is not None:
        r = oui_entries.by_country_code(a.country_code)
    elif a.country_name is not None:
        r = oui_entries.by_country_name(a.country_name)

    if r is None:
        log.error("could not find entry!")
    else:
        log.info(r.__dict__)


if __name__ == '__main__':
    main()
