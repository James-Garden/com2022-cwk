import socket
import signal
import selectors
import types


# Defining constants
HOST = "127.0.0.1"  # The hostname of this server
PORT = 65432  # The port of this server

# Defining global variables
event_state = False
sel = selectors.DefaultSelector()


def exit_handler(signum, frame):  # Stopping the server gracefully
    print("Stopping server.")
    try:
        sel.close()
    finally:
        exit(0)


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Accept connection from client
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    cli_events = selectors.EVENT_READ | selectors.EVENT_WRITE  # The events the selector should monitor for this object
    sel.register(conn, cli_events, data=data)  # Add the connection to this client to the selector


def service_connection(key, mask):
    sock = key.fileobj  # Get the socket object for this client - previously called conn
    data = key.data  # Get the data

    if mask & selectors.EVENT_READ:  # If the socket has a read event pending
        recv_data = sock.recv(1024)  # Socket should be ready to read data
        if recv_data:  # If something was received
            data.outb += recv_data  # Add the received data to the output data (FOR PINGING)

        else:  # If no data was received this means the client has closed their socket
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:  # If the socket has a write event pending
        if data.outb:  # If there is something to send
            print(f"Echoing {data.outb!r} to {data.addr}")  # (NEXT 2 LINES FOR PING SERVER)
            sent = sock.send(data.outb)  # Send some number of bytes from data.outb to the client
            data.outb = data.outb[sent:]  # Remove the number of bytes sent from data.outb


if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_handler)  # Registering the exit_handler to SIGINT (CTRL + C)
    print("Starting server. Stop with (CTRL + C)\n")

    sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket listening for incoming connections
    sock_listen.bind((HOST, PORT))  # Binding listening socket to host and port defined above
    sock_listen.listen()  # Telling the socket to start listening
    print(f"Listening on {(HOST, PORT)}")
    sock_listen.setblocking(False)  # Allow multiple simultaneous connections to listening socket

    # Selector will monitor listening socket for read events (EVENT_READ)
    sel.register(sock_listen, selectors.EVENT_READ, data=None)

    while True:
        events = sel.select(timeout=None)  # Block until a monitor object is ready
        # Key is a tuple which contains the socket: key.fileobj, and the data from that socket: key.data
        # and mask is a bitmask of the operations that are ready, i.e. EVENT_READ and/or EVENT_WRITE
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)

