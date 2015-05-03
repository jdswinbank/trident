#!/usr/bin/env python

import argparse
import asyncio
import contextlib
import sys

import lxml.etree as etree
from trident.net import send_prefixed_bytes, receive_prefixed_bytes

@asyncio.coroutine
def voevent_sender(message, host, port):
    reader, writer = yield from asyncio.open_connection(host, port)
    yield from send_prefixed_bytes(writer, message)
    response = yield from receive_prefixed_bytes(reader)
    writer.close()
    return response

def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='Destination host', default="localhost")
    parser.add_argument('--port', help='Destination port', default="8098")
    parser.add_argument('--file', help='Path to event text')
    return parser.parse_args(args)

def read_event(source):
    if source:
        f = open(source, 'rb')
    else:
        f = sys.stdin.buffer
    try:
        return etree.fromstring(f.read())
    finally:
        f.close()

def good_response(response, host, port):
    element = etree.fromstring(response)
    if element.get('role') == 'ack':
        return True
    if element.get('role') == 'nak':
        print("Nak received: {}:{} refused to accept VOEvent ({})".format(
              host, port, element.findtext("Meta/Result",
                                           default="no reason given")))
        return False

if __name__ == "__main__":
    config = parse_args()
    element = read_event(config.file)
    message = etree.tostring(element, xml_declaration=True, encoding='UTF-8')

    with contextlib.closing(asyncio.get_event_loop()) as loop:
        response = loop.run_until_complete(voevent_sender(message, config.host,
                                                          config.port))

    if not good_response(response, config.host, config.port):
        sys.exit(1)
