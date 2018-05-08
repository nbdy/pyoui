from sys import argv

from os.path import isdir

import dump
import mongodbInserter
import redisInserter
import sqliteInserter


def _help():
    print "usage: python oui.py [arguments]"
    print "optional:"
    print "\t-d\t--dump\t\tdownload csv's from ieee.org"
    print "\t-dd\t--directory\tdirectory to r/w csv's from/to"
    print "\t-db\t--dbms\t\tsqlite/mongodb/redis"
    print "that's it"
    exit()


args = {
    "dump": False,
    "directory": "csv/",
    "dbms": "sqlite"
}

i = 0
while i < len(argv):
    if argv[i] == "-d" or argv[i] == "--dump":
        args["dump"] = True
    elif argv[i] == "-dd" or argv[i] == "--directory":
        args["directory"] = argv[i + 1]
    elif argv[i] == "-db" or argv[i] == "--dbms":
        args["dbms"] = argv[i + 1]
    elif argv[i] == "-h" or argv[i] == "--help":
        _help()
    i += 1

args["dump"] = not isdir(args["directory"])
if args["dump"]:
    dump.dump(args["directory"])

if args["dbms"] == "mongodb":
    mongodbInserter.dir_2_mongodb(args["directory"])
elif args["dbms"] == "sqlite":
    sqliteInserter.dir_2_sqlite(args["directory"])
elif args["dbms"] == "redis":
    redisInserter.dir_2_redis(args["directory"])
