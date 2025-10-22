# pyoui

[![CodeFactor](https://www.codefactor.io/repository/github/nbdy/pyoui/badge/master)](https://www.codefactor.io/repository/github/nbdy/pyoui/overview/master)

## Installation

- Pip (users):
  ```bash
  pip install pyoui
  ```
- uv (inside your project):
  ```bash
  uv add pyoui
  ```
- Install from the main branch:
  ```bash
  pip install git+https://github.com/nbdy/pyoui
  ```

## CLI usage

Run:
```bash
pyoui --help
```

Options:
- -o, --outfile: file path for the downloaded IEEE OUI text file
- -d, --debug: enable debug logging
- -p, --prefix: search by MAC prefix (e.g., 00:22:72)
- -org, --organization: search by organization name
- -cc, --country-code: search by 2-letter country code (e.g., US)
- -cn, --country-name: search by country name (e.g., United States)

Examples:
```bash
pyoui -p 00:22:72
pyoui -org "national security"
pyoui -cc US
```

#### ... use by code:

```python
from pyoui import OUI

entries = OUI(debug=True).parse()

print("entries:", entries.size())

e = next(entries.by_organization("national security"))
print("organization", e.organization.__dict__, e.prefix)

e = next(entries.by_prefix("00:22:72"))
print("prefix", e.organization.__dict__, e.prefix)

e = next(entries.by_mac("BC:23:92:42:42:42"))
print("mac", e.organization.__dict__, e.prefix)

e = list(entries.by_country_code("US"))
print("length:", len(e))
print("first item:", e[0].prefix, e[0].organization.__dict__)

ae = list(entries.by_country_name("United States"))
print("by country code length:", len(e), " | by name length:", len(ae))
print("lengths should be equal")
```


## Development

This project uses uv for dependency management and builds.

- Create and sync a virtual environment:
  ```bash
  uv venv
  uv sync
  ```
- Run tests:
  ```bash
  uv run pytest
  ```
- Build the package (sdist and wheel):
  ```bash
  uv build
  ```
- Run the CLI without installing:
  ```bash
  uv run pyoui --help
  ```

## Publishing

Releases are published automatically to PyPI via GitHub Actions using PyPI Trusted Publishing.

- Create a GitHub release (or trigger the workflow manually). Upon a published release, the workflow will:
  - Build the package with `uv build`.
  - Upload the artifacts to PyPI using `pypa/gh-action-pypi-publish` with OpenID Connect (OIDC).

To enable trusted publishing, ensure the PyPI project is configured to trust this GitHub repository.
See: https://github.com/pypa/gh-action-pypi-publish
