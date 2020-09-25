#!/usr/bin/env python3

import argparse
import datetime
import asyncio
from collections import defaultdict
import random

import pymysql
from telethon import TelegramClient
from telethon.tl import types, functions

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--api-id', type=str, required=True)
    p.add_argument('--api-hash', type=str, required=True)
    p.add_argument('--database', type=str, required=True)
    p.add_argument('--host', type=str, default='localhost')
    p.add_argument('--port', type=int, default='3306')
    p.add_argument('--user', type=str, default='root')
    p.add_argument('--password', type=str)
    p.add_argument('--batch', type=int, default=5000)
    return p.parse_args()

def uncutnum(num):
    return '+' + str(79000000000 + num)

def cutnum(num):
    return int(num) - 79000000000

def select_contacts(cursor, limit):
    cursor.execute('SELECT cutnum FROM nums WHERE tgid IS NULL '
                   'ORDER BY RAND() LIMIT %s', limit)
    return [uncutnum(record[0]) for record in cursor]

def mark_processed(cursor, contacts):
    cursor.executemany(
        'UPDATE nums SET tgid = %s WHERE cutnum = %s',
        contacts)

async def update_roster(client, contacts):
    await client(functions.contacts.ImportContactsRequest(
        contacts=[
            types.InputPhoneContact(
                client_id=random.randrange(-2**63, 2**63),
                phone=contact,
                first_name=contact,
                last_name='')
            for contact in contacts]))

async def receive_ids(client, contacts):
    roster = await client(functions.contacts.GetContactsRequest(hash=0))
    roster = [(x.id, cutnum(x.phone)) for x in roster.users]
    found = [x[1] for x in roster]
    roster.extend([(0, cutnum(x)) for x in contacts if not cutnum(x) in found])
    return roster

async def cleanup_roster(client):
    roster = await client(functions.contacts.GetContactsRequest(hash=0))
    await client(functions.contacts.DeleteContactsRequest(id=roster.users))

async def main(args):
    connection = pymysql.connect(host=args.host,
                                 user=args.user,
                                 password=args.password,
                                 db=args.database,
                                 charset='utf8mb4')
    cursor = connection.cursor()

    t = datetime.datetime.now()
    contacts = select_contacts(cursor, args.batch)
    print('select: ' + str((datetime.datetime.now() - t).total_seconds()))

    async with TelegramClient('tgyp', args.api_id, args.api_hash) as client:
        await update_roster(client, contacts)
        contacts = await receive_ids(client, contacts)
        await cleanup_roster(client)

    t = datetime.datetime.now()
    mark_processed(cursor, contacts)
    connection.commit()
    print('update: ' + str((datetime.datetime.now() - t).total_seconds()))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(parse_args()))
