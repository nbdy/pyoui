import json

try:
    import progressbar

    PROGRESSBAR_DISABLED = False
except ImportError:
    print "[W] pip install progressbar"
    PROGRESSBAR_DISABLED = True

import redis

from helper import read_csv_2_list, listdir_execute


def process_row(row, r):
    data = {}
    for k in row.keys():
        data[k.lower().replace(" ", "")] = row.get(k)
    r.set("oui." + row["Assignment"], json.dumps(data))


def csv_2_redis(csv_file):
    rows = read_csv_2_list(csv_file)
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    if not PROGRESSBAR_DISABLED:
        bar = progressbar.ProgressBar()
        for row in bar(rows):
            process_row(row, r)
    else:
        for row in rows:
            process_row(row, r)


def dir_2_redis(dir="csv/"):
    listdir_execute(dir, csv_2_redis)


if __name__ == '__main__':
    dir_2_redis()
