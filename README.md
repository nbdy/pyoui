# 🛡️ pyoui

[![CodeFactor](https://www.codefactor.io/repository/github/nbdy/pyoui/badge/master)](https://www.codefactor.io/repository/github/nbdy/pyoui/overview/master)

**pyoui** is a lightweight Python utility to lookup and parse the IEEE OUI (Organizationally Unique Identifier) database. Easily identify network device vendors by their MAC addresses or search through the IEEE registry.

## ✨ Features

- 🔍 **Flexible Search:** Lookup by MAC address, prefix, organization name, or country.
- 🚀 **CLI & Library:** Use it as a standalone tool or a Python package.
- 📅 **Auto-Managed Data:** Automatically downloads and caches the latest IEEE OUI data.
- 🛠️ **Modern Tooling:** Built with `uv`, `ruff`, and type hints.

## 🚀 Installation

### For Users
```bash
pip install pyoui
```

### For Developers (using `uv`)
```bash
uv add pyoui
```

### From Source
```bash
pip install git+https://github.com/nbdy/pyoui
```

## 📖 Usage

### Command Line Interface

Quickly search the OUI database from your terminal:

```bash
# Search by MAC prefix
pyoui --prefix 00:22:72

# Search by organization name
pyoui --organization "national security"

# Search by country code (ISO 3166-1 alpha-2)
pyoui --country-code US
```

Run `pyoui --help` to see all available flags and options (like output formats: JSON, CSV, Table).

### Python API

Integrate `pyoui` into your own scripts:

```python
from pyoui import OUI

# Initialize and parse the OUI data
# It will download the database if it doesn't exist or is older than 30 days
entries = OUI().parse()

# Lookup by MAC address
entry = next(entries.by_mac("BC:23:92:42:42:42"))
print(f"Vendor: {entry.organization.name}")

# Search by organization name
for entry in entries.by_organization("national security"):
    print(f"{entry.prefix} -> {entry.organization.name}")

# Filter by country
us_entries = list(entries.by_country_code("US"))
print(f"Found {len(us_entries)} US-based organizations.")
```

## 🧑‍💻 Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nbdy/pyoui.git
   cd pyoui
   ```

2. **Sync dependencies:**
   ```bash
   uv sync
   ```

3. **Install pre-commit hooks:**
   We use `pre-commit` to ensure code quality.
   ```bash
   uv run pre-commit install
   ```

### Common Tasks

- **Run Tests:** `uv run pytest`
- **Lint Code:** `uv run ruff check .`
- **Build Package:** `uv build`
- **Run CLI locally:** `uv run pyoui --help`
