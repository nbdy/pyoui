import csv
from os import listdir


def read_csv_2_list(csv_file):
    rows = []
    with open(csv_file, 'rb') as c:
        cr = csv.DictReader(c)
        for row in cr:
            rows.append(row)
    return rows


def listdir_execute(d, c):
    if not d.endswith("/"):
        d += "/"
    for csv_file in listdir(d):
        csv_file = d + csv_file
        c(csv_file)


if __name__ == '__main__':
    print "don't execute this script directly"
