from ouilookup import OUI

entries = OUI(debug=True).parse()
print("entries:", entries.size())
e = next(entries.by_company("national security"))
print("company", e.company.__dict__, e.prefix)
e = next(entries.by_prefix("00:22:72"))
print("prefix", e.company.__dict__, e.prefix)
e = next(entries.by_mac("BC:23:92:42:42:42"))
print("mac", e.company.__dict__, e.prefix)
