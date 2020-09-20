#!/usr/bin/env python3

import csv
import argparse
import pymysql

TRDICT = {}

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--input-file', type=argparse.FileType('r'), required=True)
    p.add_argument('--database', type=str, required=True)
    p.add_argument('--host', type=str, default='localhost')
    p.add_argument('--port', type=int, default='3306')
    p.add_argument('--user', type=str, default='root')
    p.add_argument('--password', type=str)
    return p.parse_args()

def cutnum(code, num):
    return (code - 900) * 10000000 + num

def expand_trdict(filename):
    global TRDICT
    with open(filename, 'r') as f:
        for line in f.readlines():
            line = line.strip().split(':')
            TRDICT[line[0].strip()] = line[1].strip()

def translate(string):
    return TRDICT[string]


if __name__ == '__main__':
    args = parse_args()
    expand_trdict('telcos.txt')
    expand_trdict('regions.txt')

    numreader = csv.reader(args.input_file, delimiter=';')
    connection = pymysql.connect(host=args.host,
                                 user=args.user,
                                 password=args.password,
                                 db=args.database,
                                 charset='utf8mb4')
    cursor = connection.cursor()
    

    for row in numreader:
        try:
            code = int(row[0])
            first = int(row[1])
            last = int(row[2])
            capacity = int(row[3])
            telco = translate(row[4])
            region = translate(row[5])
        except ValueError:
            continue
        else:
            batch = []
            query = ('INSERT INTO `nums` (`cutnum`, `telco`, `region`) '
                     'VALUES (%s, %s, %s)')
            while first <= last:
                batch.append((cutnum(code, first), telco, region))
                first += 1
            cursor.executemany(query, batch)
            connection.commit()
