"""The main entry point for pyoui."""

import csv
import sys
from argparse import ArgumentParser
from pathlib import Path
from tempfile import gettempdir

from loguru import logger as log
from rich.console import Console
from rich.table import Table

from pyoui import OUI


def main():
    """Run the CLI."""
    ap = ArgumentParser()
    ap.add_argument(
        "-o",
        "--outfile",
        default=str(Path(gettempdir()) / "oui.txt"),
        help="oui file which will be downloaded and read.",
    )
    ap.add_argument("-d", "--debug", action="store_true", help="enable debugging")
    ap.add_argument("-p", "--prefix", help="search by mac prefix")
    ap.add_argument("-m", "--mac", help="search by mac address")
    ap.add_argument("-org", "--organization", help="search by organization name")
    ap.add_argument("-cc", "--country-code", help="search by country code")
    ap.add_argument("-cn", "--country-name", help="search by country name")
    ap.add_argument("-u", "--update", action="store_true", help="force update of the OUI database")
    ap.add_argument("--url", help="custom OUI source URL")
    ap.add_argument(
        "-f",
        "--format",
        choices=["log", "json", "csv", "table"],
        default="log",
        help="output format (default: log)",
    )
    a = ap.parse_args()

    log.remove()
    log.add(
        sys.stderr,
        level="DEBUG" if a.debug else "INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | <level>{message}</level>",
    )

    try:
        oui = OUI(outfile=a.outfile, debug=a.debug, force_update=a.update, url=a.url)
        oui_entries = oui.parse()
    except Exception as ex:
        log.error(f"Failed to load OUI database: {ex}")
        return 1

    r = None
    if a.prefix is not None:
        r = oui_entries.by_prefix(a.prefix)
    elif a.mac is not None:
        r = oui_entries.by_mac(a.mac)
    elif a.organization is not None:
        r = oui_entries.by_organization(a.organization)
    elif a.country_code is not None:
        r = oui_entries.by_country_code(a.country_code)
    elif a.country_name is not None:
        r = oui_entries.by_country_name(a.country_name)

    if r is None:
        log.error("No search parameter provided")
        return 1

    results = list(r)
    if not results:
        log.error("Could not find any matching entry!")
        return 1

    console = Console()

    if a.format == "log":
        for e in results:
            org_info = e.organization.__dict__ if e.organization else {}
            log.info(f"{e.prefix} -> {org_info}")
    elif a.format == "json":
        output = []
        for e in results:
            item = {"prefix": e.prefix}
            if e.organization:
                item["organization"] = e.organization.__dict__
            output.append(item)
        console.print_json(data=output)
    elif a.format == "csv":
        writer = csv.writer(sys.stdout)
        writer.writerow(["Prefix", "Name", "Street", "District", "Country"])
        for e in results:
            if e.organization:
                writer.writerow(
                    [
                        e.prefix,
                        e.organization.name,
                        e.organization.street,
                        e.organization.district,
                        e.organization.country,
                    ]
                )
            else:
                writer.writerow([e.prefix, "", "", "", ""])
    elif a.format == "table":
        table = Table(title="OUI Search Results")
        table.add_column("Prefix", style="cyan", no_wrap=True)
        table.add_column("Organization", style="magenta")
        table.add_column("Country", style="green")

        for e in results:
            name = (e.organization.name or "") if e.organization else ""
            country = (e.organization.country or "") if e.organization else ""
            table.add_row(e.prefix, name, country)

        console.print(table)

    return 0


if __name__ == "__main__":
    main()
