import signal
import websockets
import asyncio

# Defining constants
HOST = "127.0.0.1"  # The hostname of this server
PORT = 1234  # The port of this server


def exit_handler(signum, frame):  # Stopping the server gracefully
    print("Stopping server.")
    try:
        pass
    finally:
        exit(0)


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []                          # Array of connected clients
        self.client_names = {}
        self.clients_awaiting_response = []        # Array of clients server is waiting for a response from
        self.clients_responded = []                # Array of clients that have responded and their response
        self.host_client = None                    # The client hosting an event
        self.event_state = False                   # Whether the server has an active invitation
        self.valid_users = [
            ("james_g", "garden"),
            ("james_t", "titman"),
            ("markos", "doufos"),
            ("spyros", "kalodikis")]               # Valid usernames and passwords
        # Hardcoded response messages
        self.welcome_msg = b"Hello!"               # Sent on successful connection
        self.event_state_msg = b"P_EVENT_EXISTS"   # Sent if a user sends an invitation while in event state
        self.not_event_state_msg = b"P_NO_EVENT"   # Sent if a user responds while not in event state
        self.event_end_msg = b"P_EVENT_END"        # Sent when all responses to an event have been collected
        self.own_event_msg = b"P_YOUR_EVENT"       # Sent if a user attempts to respond to their own event
        self.ok_msg = b"P_OK"
        self.current_event_msg = None              # Sent once a user plans an event

    def start(self):
        asyncio.run(self.run())

    async def run(self):
        async with websockets.serve(self.connection_handler, self.host, self.port):
            while True:
                while not self.event_state:    # Wait until server enters event state
                    await asyncio.sleep(0.01)  # Wait 0.01s and check if in event state

                # Once server enters event state
                for sock in self.clients:             # Go through all the connected clients
                    if not sock == self.host_client:  # If the current client is not the one that sent the invitation
                        await sock.send(self.current_event_msg)   # Send the invitation

                self.clients_awaiting_response = self.clients.copy()  # Await a response from
                self.clients_awaiting_response.remove(self.host_client)

                while len(self.clients_awaiting_response) != 0:  # Wait for all clients to respond
                    await asyncio.sleep(0.1)

                self.event_state = False  # Once all responses have been recorded, exit event state

                await asyncio.sleep(0.1)  # Wait a short time in case an updated response is still being handled

                responses = "Responses have been collected:\n"
                for response in self.clients_responded:
                    sock = response[0]
                    answer = response[1]
                    user = self.client_names[sock]  # Get the clients' username based on their websocket
                    if answer:
                        responses += f"{user}: Yes\n"
                    else:
                        responses += f"{user}: No\n"

                websockets.broadcast(self.clients, responses.encode())

                # Reset server state to allow for new invite
                self.host_client = None
                self.clients_responded = []
                self.clients_awaiting_response = []

    # When a client connects send a welcome message, then wait for them to send something
    async def connection_handler(self, websocket):
        try:
            print(f"Connected by {websocket.remote_address}")
            auth_packet = await websocket.recv()
            auth = auth_packet.decode().split(":")

            if auth[0] != "P_AUTH":
                raise ValueError("Invalid auth packet format")

            username = None
            for valid_user in self.valid_users:
                if auth[1] == valid_user[0] and auth[2] == valid_user[1]:  # If username *and* password match
                    username = auth[1]
                    break

            if username is None:  # If no match was found
                raise AssertionError("Invalid username or password")

            self.client_names[websocket] = username
            self.clients.append(websocket)          # Add the client to the list of clients
            await websocket.send(self.welcome_msg)  # Send greeting message on successful connection
            while True:
                data = await websocket.recv()
                data = data.decode().split(":")
                msg_type = data[0]
                is_host = websocket == self.host_client
                # If the server is in an event state
                if self.event_state:

                    if msg_type == "P_GO_OUT":                      # Client has sent an invalid invitation
                        await websocket.send(self.event_state_msg)  # Send invalid invitation packet (P_EVENT_EXISTS)
                    # Client has sent a potentially valid response
                    elif msg_type == "P_YES" or msg_type == "P_NO":
                        # If the client is the host and tries to respond to their own invitation
                        if is_host:
                            await websocket.send(self.own_event_msg)  # Send invalid response packet (P_YOUR_EVENT)
                        else:
                            try:  # Try to remove the client from the list of clients awaiting response
                                # If this is their first response, then this will work
                                self.clients_awaiting_response.remove(websocket)
                            except ValueError:  # If this is not their first response
                                for client_response in self.clients_responded:  # Go through the clients that have responded

                                    if client_response[0] == websocket:  # Once it finds its previous response
                                        self.clients_responded.remove(client_response)  # Remove the old response
                                        break  # Exit the loop
                            finally:  # Record the clients response
                                if msg_type == "P_YES":  # If the client responds affirmatively
                                    response = True
                                else:                    # If the client responds negatively
                                    response = False
                                self.clients_responded.append((websocket, response))

                # If the server is *not* in an event state
                else:
                    if msg_type == "P_GO_OUT":                      # Client has sent a valid invitation
                        self.event_state = True                     # Put the server into an event state
                        self.host_client = websocket                # Set this client as the host of the event
                        self.current_event_msg = ("P_INVITATION:"+":".join(data[1:])).encode()
                        self.clients_responded.append((websocket, True))
                        is_host = True
                        await websocket.send(self.ok_msg)           # Send ack packet (P_OK)
                    if msg_type == "P_YES" or msg_type == "P_NO":
                        # Inform the user that there is no invitation to answer (P_NO_EVENT)
                        await websocket.send(self.not_event_state_msg)

        except websockets.ConnectionClosed:  # Cleanup if the client disconnects
            print(f"Lost connection to client at {websocket.remote_address}")
            self.clients.remove(websocket)  # Remove the client from the list of connected clients
            del self.client_names[websocket]
            # This block attempts to remove this client from the list of clients the server is waiting for,
            # if this client has already responded or the server is not in an event state then the client will not be
            # in this list and will throw a ValueError
            try:
                self.clients_awaiting_response.remove(websocket)
            except ValueError:
                pass

        except ValueError as msg:
            print(msg)
            await websocket.send(b"Error: Invalid auth packet format")

        except AssertionError as msg:
            print(msg)
            await websocket.send(b"Error: Unauthorised user - check username and password")


if __name__ == "__main__":
    # Registering the exit_handler to SIGINT (CTRL + C)

    signal.signal(signal.SIGINT, exit_handler)
    print("Starting server. Stop with (CTRL + C)\n")

    server = Server(HOST, PORT)  # Initialising the server
    server.start()               # Starting the server
