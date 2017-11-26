import urllib
from os.path import isfile, isdir
from os import makedirs, listdir
import csv
import pymongo
import progressbar

URLS = [
    "https://standards.ieee.org/develop/regauth/oui/oui.csv",
    "https://standards.ieee.org/develop/regauth/oui28/mam.csv",
    "https://standards.ieee.org/develop/regauth/oui36/oui36.csv",
    "https://standards.ieee.org/develop/regauth/cid/cid.csv",
    "https://standards.ieee.org/develop/regauth/ethertype/eth.csv",
    "https://standards.ieee.org/develop/regauth/manid/manid.csv",
    "https://standards.ieee.org/develop/regauth/bopid/opid.csv",
    "https://standards.ieee.org/develop/regauth/iab/iab.csv"
]

FILE_DIRECTORY = "csv/"


def load(url, csv_file):
    if not isfile(csv_file):
        try:
            urllib.urlretrieve(url, csv_file)
        except IOError as e:
            print e.message


def csv_to_mongodb(csv_file):
    col = csv_file.split(".")[0]
    rows = []
    with open(csv_file, 'rb') as c:
        cr = csv.DictReader(c)
        for row in cr:
            rows.append(row)

    mc = pymongo.MongoClient()
    db = mc.get_database("oui")
    db.drop_collection(col)
    db.create_collection(col)
    cl = db.get_collection(col)
    print "inserting", len(rows), "identifiers into", col
    bar = progressbar.ProgressBar()
    for row in bar(rows):
        cl.insert_one(row)


if not isdir(FILE_DIRECTORY):
    makedirs(FILE_DIRECTORY)

print "downloading", len(URLS), "urls."
bar = progressbar.ProgressBar()
for url in bar(URLS):
    csv_file = FILE_DIRECTORY + url.split("/")[-1]
    load(url, csv_file)

print "inserting", len(listdir(FILE_DIRECTORY)), "collections."
for csv_file in listdir(FILE_DIRECTORY):
    csv_file = FILE_DIRECTORY + csv_file
    csv_to_mongodb(csv_file)
