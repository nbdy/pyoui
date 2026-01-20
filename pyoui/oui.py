"""Core OUI lookup logic."""

import re
import time
from dataclasses import dataclass
from pathlib import Path
from tempfile import gettempdir
from typing import Dict, Iterator, List, Optional

from loguru import logger as log
from pycountry import countries
from requests import RequestException, get
from tqdm import tqdm


@dataclass
class Organization:
    """Represents an organization associated with an OUI.

    Attributes:
        name (str): The name of the organization.
        street (Optional[str]): Street address of the organization.
        district (Optional[str]): District or city/state/zip of the organization.
        country (Optional[str]): Two-letter country code of the organization.

    """

    name: str
    street: Optional[str] = None
    district: Optional[str] = None
    country: Optional[str] = None


@dataclass
class OuiEntry:
    """Represents a single OUI entry.

    Attributes:
        prefix (str): The MAC prefix (e.g., "00:22:72").
        organization (Optional[Organization]): The organization associated with this prefix.

    """

    prefix: str
    organization: Optional[Organization] = None

    def __post_init__(self):
        """Normalize the prefix after initialization."""
        if self.prefix:
            self.prefix = self.prefix.replace("-", ":").upper()


class OuiEntries:
    """A collection of OUI entries parsed from a file."""

    def __init__(self, infile: str, debug: bool = False):
        """Initialize the collection by parsing the input file.

        Args:
            infile (str): Path to the OUI text file.
            debug (bool): Enable debug logging. Defaults to False.

        """
        self.entries: List[OuiEntry] = self.parse(infile, debug=debug)
        self._country_cache: Dict[str, str] = {}
        self._prefix_map: Dict[str, List[OuiEntry]] = {}
        self._country_map: Dict[str, List[OuiEntry]] = {}

        for e in self.entries:
            # Populate prefix map
            if e.prefix not in self._prefix_map:
                self._prefix_map[e.prefix] = []
            self._prefix_map[e.prefix].append(e)

            # Populate country map
            if e.organization and e.organization.country:
                cc = e.organization.country.upper()
                if cc not in self._country_map:
                    self._country_map[cc] = []
                self._country_map[cc].append(e)

    @staticmethod
    def parse(filename: str, debug: bool = False) -> List[OuiEntry]:
        """Parse the OUI file.

        Args:
            filename (str): The file to parse.
            debug (bool): Enable debug logging.

        Returns:
            List[OuiEntry]: A list of parsed OUI entries.

        """
        if debug:
            log.debug(f"Parsing entries from {filename}")
        lst: List[OuiEntry] = []
        with open(filename, encoding="utf-8") as i:
            current_entry: Optional[OuiEntry] = None
            current_org: Optional[Organization] = None
            # line_counter tracks lines after the (hex) line
            # -1: searching for (hex)
            # 0: just found (hex), next is blank
            # 1: next is street
            # 2: next is district
            # 3: next is country
            line_counter = -1

            for _ in i:
                line = _.rstrip("\n")
                if "(hex)" in line:
                    # Save previous if it exists (though the state machine should handle it)
                    # prefix is always first 8 chars; organization follows '(hex)'
                    prefix = line[0:8].strip()
                    org_name = line.split("(hex)", 1)[1].strip()
                    current_org = Organization(name=org_name)
                    current_entry = OuiEntry(prefix=prefix, organization=current_org)
                    line_counter = 0
                    continue

                if line_counter == 0:  # Blank line after (hex)
                    line_counter = 1
                elif line_counter == 1:  # Street
                    if current_org:
                        current_org.street = line.strip()
                    line_counter = 2
                elif line_counter == 2:  # District
                    if current_org:
                        current_org.district = line.strip()
                    line_counter = 3
                elif line_counter == 3:  # Country
                    if current_org:
                        current_org.country = line.strip()
                    if current_entry:
                        lst.append(current_entry)
                    line_counter = -1

        return lst

    @staticmethod
    def is_valid_mac(mac: str) -> bool:
        """Check if a MAC address is valid.

        Args:
            mac (str): The MAC address to check.

        Returns:
            bool: True if valid, False otherwise.

        """
        if not mac:
            return False
        # Supports formats like AA:BB:CC:DD:EE:FF, AA-BB-CC-DD-EE-FF, AABBCCDDEEFF
        # and also shorter forms if they are meant to be prefixes.
        # But here we specifically check for a full MAC.
        pattern = re.compile(r"^([0-9A-Fa-f]{2}[:-]?){5}([0-9A-Fa-f]{2})$")
        return bool(pattern.match(mac))

    @staticmethod
    def is_valid_prefix(prefix: str) -> bool:
        """Check if a MAC prefix is valid.

        Args:
            prefix (str): The MAC prefix to check.

        Returns:
            bool: True if valid, False otherwise.

        """
        if not prefix:
            return False
        # Supports formats like AA:BB:CC, AA-BB-CC, AABBCC
        pattern = re.compile(r"^([0-9A-Fa-f]{2}[:-]?){2}([0-9A-Fa-f]{2})$")
        return bool(pattern.match(prefix))

    def by_mac(self, mac: str) -> Iterator[OuiEntry]:
        """Search for entries by MAC address.

        Args:
            mac (str): The MAC address to search for.

        Yields:
            Iterator[OuiEntry]: Matching OUI entries.

        """
        if not self.is_valid_mac(mac):
            if mac:
                log.warning(f"Invalid MAC address: {mac}")
            return
        n_mac = mac.replace("-", ":").upper()
        # For OUI (MA-L), the prefix is the first 8 characters (XX:XX:XX)
        prefix = n_mac[:8]
        if prefix in self._prefix_map:
            yield from self._prefix_map[prefix]

    def by_prefix(self, prefix: str) -> Iterator[OuiEntry]:
        """Search for entries by MAC prefix.

        Args:
            prefix (str): The MAC prefix to search for.

        Yields:
            Iterator[OuiEntry]: Matching OUI entries.

        """
        if not self.is_valid_prefix(prefix):
            if prefix:
                log.warning(f"Invalid MAC prefix: {prefix}")
            return
        n_prefix = prefix.replace("-", ":").upper()
        if n_prefix in self._prefix_map:
            yield from self._prefix_map[n_prefix]

    def by_organization(self, name: str) -> Iterator[OuiEntry]:
        """Search for entries by organization name.

        Args:
            name (str): The organization name (partial match, case-insensitive).

        Yields:
            Iterator[OuiEntry]: Matching OUI entries.

        """
        if not name:
            return
        low = name.lower()
        for e in self.entries:
            if e.organization and e.organization.name and low in e.organization.name.lower():
                yield e

    def by_country_name(self, name: str) -> Iterator[OuiEntry]:
        """Search for entries by country name.

        Args:
            name (str): The country name.

        Yields:
            Iterator[OuiEntry]: Matching OUI entries.

        """
        if not name:
            return iter(())

        if name in self._country_cache:
            return self.by_country_code(self._country_cache[name])

        try:
            cc = countries.search_fuzzy(name)[0].alpha_2
            self._country_cache[name] = cc
            return self.by_country_code(cc)
        except LookupError:
            # empty iterator for unknown country names
            return iter(())

    def by_country_code(self, cc: str) -> Iterator[OuiEntry]:
        """Search for entries by two-letter country code.

        Args:
            cc (str): The two-letter country code.

        Yields:
            Iterator[OuiEntry]: Matching OUI entries.

        """
        if not cc or len(cc) != 2:
            return
        ncc = cc.upper()
        if ncc in self._country_map:
            yield from self._country_map[ncc]

    def size(self) -> int:
        """Return the number of loaded entries.

        Returns:
            int: The number of entries.

        """
        return len(self.entries)


class OUI:
    """Handles downloading and loading the OUI database."""

    OUI_URL: str = "https://standards-oui.ieee.org/oui.txt"

    def __init__(
        self,
        outfile: str = str(Path(gettempdir()) / "oui.txt"),
        debug: bool = False,
        max_age: int = 2592000,
        force_update: bool = False,
        url: Optional[str] = None,
    ):
        """Initialize the OUI handler.

        Args:
            outfile (str): Path where the OUI file will be saved.
            debug (bool): Enable debug logging.
            max_age (int): Maximum age of the local file in seconds (default 30 days).
            force_update (bool): If True, always download the file.
            url (Optional[str]): Custom OUI source URL. Defaults to IEEE's OUI URL.

        """
        self.outfile = outfile
        self.debug = debug
        self.max_age = max_age
        self.url = url or self.OUI_URL
        self.load(force=force_update)

    def load(self, force: bool = False):
        """Download the OUI file if it doesn't exist, is too old, or force is True.

        Args:
            force (bool): If True, always download the file.

        Raises:
            RequestException: If the download fails.
            IOError: If saving the file fails.

        """
        should_download = force or not Path(self.outfile).is_file()

        if not should_download and self.max_age > 0:
            file_age = time.time() - Path(self.outfile).stat().st_mtime
            if file_age > self.max_age:
                if self.debug:
                    log.debug(
                        f"File {self.outfile} is older than {self.max_age} seconds. Re-downloading."
                    )
                should_download = True

        if should_download:
            if self.debug:
                log.debug(f"Downloading {self.url} to {self.outfile}")
            try:
                r = get(self.url, timeout=30, stream=True)
                r.raise_for_status()
                total_size = int(r.headers.get("content-length", 0))
                with open(self.outfile, "wb") as o:
                    with tqdm(
                        total=total_size,
                        unit="B",
                        unit_scale=True,
                        desc="Downloading OUI",
                        disable=not self.debug,
                    ) as pbar:
                        for chunk in r.iter_content(chunk_size=8192):
                            o.write(chunk)
                            pbar.update(len(chunk))
                # Ensure appropriate file permissions (e.g., 644)
                Path(self.outfile).chmod(0o644)
            except RequestException as ex:
                log.error(f"Failed to download OUI list: {ex}")
                raise
            except IOError as ex:
                log.error(f"Failed to save OUI list: {ex}")
                raise
        else:
            if self.debug:
                log.debug(f"{self.outfile} exists and is up to date. Not downloading.")

    def parse(self) -> OuiEntries:
        """Parse the local OUI file.

        Returns:
            OuiEntries: The parsed OUI entries.

        """
        if self.debug:
            log.debug(f"Parsing {self.outfile}")
        return OuiEntries(infile=self.outfile, debug=self.debug)
