from ouilookup import OUI

entries = OUI(debug=True).parse()
print("entries:", entries.size())
print("company", entries.by_company("national security").address)
print("prefix", entries.by_prefix("00:22:72").company)
