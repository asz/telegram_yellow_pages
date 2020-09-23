#!/usr/bin/env python3

import argparse
import datetime
import asyncio

from telethon import TelegramClient
from telethon.tl import types

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--api-id', type=str, required=True)
    p.add_argument('--api-hash', type=str, required=True)
    p.add_argument('--phone', type=str, required=True)
    p.add_argument('--firstname', type=str, required=True)
    p.add_argument('--lastname', type=str, default='')
    p.add_argument('--recipient', type=str, required=True)
    return p.parse_args()

async def send_contact(client, args):
    await client.send_file(args.recipient, types.InputMediaContact(
        phone_number=args.phone,
        first_name=args.firstname,
        last_name=args.lastname,
        vcard=''))

async def main(args):
    async with TelegramClient('tgyp', args.api_id, args.api_hash) as client:
        await send_contact(client, args)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(parse_args()))
