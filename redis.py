import json

import progressbar

import redis
from helper import read_csv_2_list, listdir_execute


def csv_2_redis(csv_file):
    rows = read_csv_2_list(csv_file)
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
    bar = progressbar.ProgressBar()
    for row in bar(rows):
        data = {}
        for k in row.keys():
            data[k.lower().replace(" ", "")] = row.get(k)
        r.set("oui." + row["Assignment"], json.dumps(data))


def dir_2_redis(dir="csv/"):
    listdir_execute(dir, csv_2_redis)


if __name__ == '__main__':
    dir_2_redis()
