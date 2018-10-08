import sqlite3

try:
    import progressbar

    PROGRESSBAR_DISABLED = False
except ImportError:
    print "[W] pip install progressbar"
    PROGRESSBAR_DISABLED = True

from jinja2 import Template

from helper import read_csv_2_list, listdir_execute, generate_keys

'''
keys:
assignment
organizationname
registry
organizationaddress
'''

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS {{table}} (
  {% for key in keys %}{{key}} TEXT NOT NULL{% if loop.index < keys|length %},{% endif %}
  {% endfor %}
);
"""

INSERT = """
INSERT INTO {{table}} ({% for key in keys %}{{key}}{% if loop.index < keys|length %}, {% endif %}{% endfor %}) 
VALUES ({% for val in values %}'{{val}}'{% if loop.index < values|length %}, {% endif %}{% endfor %});
"""


def process_row(row, c):
    ka = []
    kv = []
    for k in row.keys():
        ka.append(k)
        kv.append(row.get(k).decode('utf-8').replace("'", ''))
    c.execute(Template(INSERT).render(table=tbl, keys=generate_keys(ka), values=kv))


def csv_2_sqlite(csv_file, db="oui.db"):
    rows = read_csv_2_list(csv_file)
    tbl = csv_file.split("/")[1].split(".")[0]
    print "inserting", len(rows), "into", db, tbl
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(Template(CREATE_TABLE).render(table=tbl, keys=generate_keys(rows[0].keys())))
    if not PROGRESSBAR_DISABLED:
        bar = progressbar.ProgressBar()
        for row in bar(rows):
            process_row(row, c)
    else:
        for row in rows:
            process_row(row, c)

    conn.commit()
    conn.close()


def dir_2_sqlite(csv_dir="csv/"):
    listdir_execute(csv_dir, csv_2_sqlite)


if __name__ == '__main__':
    dir_2_sqlite()
