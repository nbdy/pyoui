## pyoui

[![CodeFactor](https://www.codefactor.io/repository/github/nbdy/pyoui/badge/master)](https://www.codefactor.io/repository/github/nbdy/pyoui/overview/master)

### how to..

#### ... install:

```shell script
pip3 install pyoui
# master branch should be stable as well
pip3 install git+https://github.com/nbdy/pyoui
```

#### ... use by cli:

```shell script
pyoui --help

usage: pyoui [-h] [-o OUTFILE] [-d] [-p PREFIX] [-c COMPANY]

optional arguments:
  -h, --help            show this help message and exit
  -o OUTFILE, --outfile OUTFILE
                        oui file which will be downloaded and read.
  -d, --debug           enable debugging
  -p PREFIX, --prefix PREFIX
                        search by mac prefix
  -c COMPANY, --company COMPANY
                        search by company name
```

#### ... use by code:

```python
from pyoui import OUI

entries = OUI(debug=True).parse()

print("entries:", entries.size())

e = next(entries.by_organization("national security"))
print("company", e.organization.__dict__, e.prefix)

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
