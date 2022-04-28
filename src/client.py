import socket
import selectors
import types

# Defining constants
HOST = "127.0.0.1"
PORT = 65432

# Defining global variables
sel = selectors.DefaultSelector()
msgs = [b"Message 1 from client.", b"Message 2 from client."]


def start_connections(num_conns):
    server_addr = (HOST,PORT)
    for i in range(0, num_conns):
        connid = i + 1
        print(f"Starting connection {connid} to {server_addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            connid=connid,
            msg_total=sum(len(m) for m in msgs),
            recv_total=0,
            messages=msgs.copy(),
            outb=b"",
        )
        sel.register(sock, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print(f"Received {recv_data.decode()} from connection {data.connid}")
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection {data.connid}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print(f"Sending {data.outb.decode()} to connection {data.connid}")
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]


if __name__ == "__main__":
    start_connections(1)

    while len(data.messages):
        events = sel.select(timeout=None)  # Block until a monitor object is ready
        # Key is a tuple which contains the socket: key.fileobj, and the data from that socket: key.data
        # and mask is a bitmask of the operations that are ready, i.e. EVENT_READ and/or EVENT_WRITE
        for key, mask in events:
            service_connection(key, mask)
