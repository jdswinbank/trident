import asyncio
import struct

@asyncio.coroutine
def receive_prefixed_bytes(reader, prefix="!I"):
    inp = yield from reader.read(struct.calcsize(prefix))
    length = struct.unpack(prefix, inp)[0]
    result = yield from reader.read(length)
    return result

@asyncio.coroutine
def send_prefixed_bytes(writer, data, prefix="!I"):
    size = struct.pack(prefix, len(data))
    writer.write(size + data)
    yield from writer.drain()
