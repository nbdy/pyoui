import sqlite3

from jinja2 import Template

from helper import read_csv_2_list, listdir_execute

'''
keys:
assignment
organizationname
registry
organizationaddress
'''

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS {{table}} (
  {% for key in keys %}
  {{key}} TEXT NOT NULL,
  {% endfor %}
);
"""

INSERT = """
INSERT INTO {{table}} ({% for key in keys %}{{key}}{% endfor %}) VALUES ({% for val in values %}{{val}}{% endfor %});
"""


def csv_2_sqlite(csv_file, db="oui.db"):
    rows = read_csv_2_list(csv_file)
    print "inserting", len(rows), "into", db
    tbl = csv_file.split("/")[1].split(".")[0]
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(Template(CREATE_TABLE).render(table=tbl, keys=rows[0].keys()))
    for row in rows:
        ka = []
        kv = []
        for k in row.keys():
            ka.append(k)
            kv.append(row.get(k))
        c.execute(Template(INSERT).render(table=tbl, keys=ka, values=kv))


def dir_2_sqlite(csv_dir="csv/"):
    listdir_execute(csv_dir, csv_2_sqlite)


if __name__ == '__main__':
    dir_2_sqlite()
