import progressbar
import pymongo

from helper import read_csv_2_list, listdir_execute


def csv_2_mongodb(csv_file):
    rows = read_csv_2_list(csv_file)
    col = csv_file.split("/")[1].split(".")[0]
    mc = pymongo.MongoClient()
    mc.drop_database("oui")
    db = mc.get_database("oui")
    cl = db.get_collection(col)
    print "inserting", len(rows), "identifiers into", col
    bar = progressbar.ProgressBar()
    for row in bar(rows):
        data = {}
        for k in row.keys():
            data[k.lower().replace(" ", "")] = row.get(k)

        try:
            cl.insert_one(data)
        except Exception as x:
            print x.message


def dir_2_mongodb(csv_dir="csv/"):
    listdir_execute(csv_dir, csv_2_mongodb)


if __name__ == '__main__':
    dir_2_mongodb()
