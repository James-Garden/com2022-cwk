import asyncio
import threading
import websockets
import time
import tkinter as tk
import tkinter.messagebox
import signal
from queue import Queue

# Defining constants
SERVER = ('127.0.0.1', 1234)  # Server hostname and port
USERNAME = "james_g"          # User login name
PASSWORD = "garden"           # User password


# The program itself
class App(tk.Tk):
    # Constructor
    def __init__(self, user, password):
        super().__init__()
        self.close_conn = False
        self.user = user
        self.password = password
        # What to do when the user closes the window
        self.protocol("WM_DELETE_WINDOW", self.close)
        # Unprocessed messages from the server
        self.server_log = Queue()
        # Messages that need to be sent to the server
        self.outbox = Queue()
        # Displayed log
        self.log = Queue()
        # Window title
        self.title("Event Planning Protocol - Client")
        # Welcome message
        self.greeting = tk.Label(text=f"Welcome, {USERNAME}", )
        # Text entry box for sending an invitation
        self.send_inv_entry = tk.Entry(width=50, justify='center')
        # Button to send invitation
        self.send_inv_button = tk.Button(
            width=15,
            height=3,
            text="Send Invitation",
            command=self.send_invite
        )
        # Box containing message from a currently active invitation
        self.active_inv_text = tk.Entry(width=50, justify='center')
        self.active_inv_text.insert('end', "No Active Invitation")
        self.active_inv_text.config(state='disabled')
        # Buttons frame
        self.button_frame = tk.Frame()
        # Button to accept an invitation
        self.yes_button = tk.Button(
            self.button_frame,
            width=8,
            height=2,
            text="Yes",
            command=self.accept_invite
        )
        # Button to reject an invitation
        self.no_button = tk.Button(
            self.button_frame,
            width=8,
            height=2,
            text="No",
            command=self.reject_invite
        )
        # Label for server response log
        self.log_label = tk.Label(text="Server Log", )
        # Log of server responses
        self.log_text = tk.Text(width=50, height=10)
        # Adding all elements to window
        self.greeting.pack()
        self.send_inv_entry.pack()
        self.send_inv_button.pack()
        self.active_inv_text.pack()
        self.button_frame.pack()
        self.yes_button.pack(side='left')
        self.no_button.pack(side='right')
        self.log_label.pack()
        self.log_text.pack()
        # Start the connection thread
        self.conn_thread = threading.Thread(target=self._connection_thread)
        self.conn_thread.daemon = True
        self.conn_thread.start()
        # Start refreshing the GUI
        self.call_id = self.after(0, self._refresh)

    # Do something when the user closes the interface
    def close(self):
        self.after_cancel(self.call_id)
        self.close_conn = True
        self.destroy()
        time.sleep(0.2)
        print("Goodbye.")

    # Send an invitation to the server
    def send_invite(self):
        msg = "P_GO_OUT:"+self.send_inv_entry.get()
        self._send(msg)

    # Accept/Reject an invitation from another user
    def accept_invite(self):
        msg = "P_YES"
        self._send(msg)

    def reject_invite(self):
        msg = "P_NO"
        self._send(msg)

    # Check for messages from the server
    def _refresh(self):
        if self.server_log.empty():  # If there is nothing to be read from the log of server messages
            self.call_id = self.after(10, self._refresh)  # Wait 0.5s then check again
        else:  # If there are messages waiting to be read
            data = self.server_log.get()
            self._update_log(data)  # Update the log section of the client
            self._process_msg(data)  # Check if an invitation has been received

            self.call_id = self.after(10, self._refresh)  # Wait 0.01s then check again

    # Update the server log output text area
    def _update_log(self, data):
        msg = f"[{time.strftime('%X')}] " + data.decode() + "\n"
        if self.log.qsize() == 10:  # If the output area of the client is full
            self.log.get()  # Remove the oldest message from the queue
            self.log.put(msg)
            for i in range(0, 10):
                pos = str(i) + '.0'
                self.log_text.insert(pos, self.log.queue[i])
        else:
            pos = str(self.log.qsize() + 1) + '.0'
            self.log_text.insert(pos, msg)

    # Do something depending on what the server sends
    def _process_msg(self, data):
        msg = data.decode()
        if "P_INVITATION" in msg:
            msg = msg.replace('P_INVITATION', '')  # Strip protocol command from message
            msg = msg.lstrip(":")
            self.active_inv_text.config(state='normal')
            self.active_inv_text.delete('0', tk.END)
            self.active_inv_text.insert('end', msg)
            self.active_inv_text.config(state='readonly')
        elif "P_EVENT_EXISTS" in msg:
            tkinter.messagebox.showerror(title="Error", message="There is already an active invitation!")
        elif "P_NO_EVENT" in msg:
            tkinter.messagebox.showerror(title="Error", message="There is no event to respond to!")
        elif "P_YOUR_EVENT" in msg:
            tkinter.messagebox.showerror(title="Error", message="You can't respond to your own event!")
        elif "P_EVENT_END" in msg:
            self.active_inv_text.config(state='normal')
            self.active_inv_text.delete('0', tk.END)
            self.active_inv_text.insert('end', "No Active Invitation")
            self.active_inv_text.config(state='disabled')

    # Put whatever data needs to be sent into the outbox
    def _send(self, data):
        payload = data.encode()
        self.outbox.put(payload)

    # CONNECTION MANAGER
    # The thread that will be run when the app is created
    def _connection_thread(self):
        asyncio.run(self._start_connection())

    async def _start_connection(self):
        try:
            # Try to start the connection
            print("Connecting to server...")
            async with websockets.connect(f"ws://{SERVER[0]}:{SERVER[1]}") as websocket:
                auth = f"P_AUTH:{self.user}:{self.password}".encode()
                await websocket.send(auth)
                print("Connected.\n")
                asyncio.create_task(self._recv_loop(websocket))  # Starting listening loop
                asyncio.create_task(self._send_loop(websocket))  # Start sending loop

                # await recv_loop_task  # Wait for the recv loop to finish (i.e. when disconnecting)
                while not self.close_conn:
                    await asyncio.sleep(0.1)

                print("Disconnecting...")
                self.close()

        except OSError:
            print(f"\nError: Unable to connect to server at {SERVER[0]}:{SERVER[1]} ")
            self.close()

    async def _recv_loop(self, websocket):
        try:
            while True:
                data = await websocket.recv()
                self.server_log.put(data)
        except websockets.ConnectionClosedOK:  # If the connection to the server is closed expectedly
            self.server_log.put(b"Error: Connection to server lost")
        except websockets.ConnectionClosed:  # If the connection to the server is closed unexpectedly
            print("\nError: Connection to server lost")
            self.server_log.put(b"Error: Connection to server lost")

    async def _send_loop(self, websocket):
        try:
            while True:
                if self.outbox.empty():
                    await asyncio.sleep(1)
                    continue
                while not self.outbox.empty():
                    payload = self.outbox.get()
                    await websocket.send(payload)
        except websockets.ConnectionClosedOK:
            self.server_log.put(b"Error: Connection to server lost")


class Login(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title = "Log In"
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.user_label = tk.Label(text="Username (optional - defaults to james_g)")
        self.user_entry = tk.Entry(width=15)
        self.pass_label = tk.Label(text="Password (optional - required with username)")
        self.pass_entry = tk.Entry(width=15)
        self.server_label = tk.Label(text="Server Hostname (optional - defaults to localhost:1234)")
        self.server_entry = tk.Entry(width=20)
        self.login_button = tk.Button(text="Log In", width=8, height=2, command=self.submit)

        self.user_label.pack()
        self.user_entry.pack()
        self.pass_label.pack()
        self.pass_entry.pack()
        self.server_label.pack()
        self.server_entry.pack()
        self.login_button.pack()

    @staticmethod
    def close():
        quit(0)

    def submit(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        server = self.server_entry.get()
        if username != "":
            global USERNAME
            global PASSWORD
            USERNAME = username
            PASSWORD = password
        if server != "":
            global SERVER
            server = server.split(':')
            try:
                SERVER = (str(server[0]), int(server[1]))
            except (IndexError, ValueError):
                server = ":".join(server)
                print(f"Error: {server} is not a valid hostname and/or port combination, defaulting to localhost:1234")
                SERVER = ('127.0.0.1', 1234)
        self.destroy()


def handler():
    app.close()  # Close the program gracefully


if __name__ == '__main__':
    # If the program is forcibly stopped using CTRL + C in the python shell itself or STOP on an IDE such as pyCharm,
    # the program should close gracefully
    signal.signal(signal.SIGINT, handler)
    # Show the login prompt
    login = Login()
    login.mainloop()
    # Create the app and connect to the server
    app = App(USERNAME, PASSWORD)
    # Show the GUI
    app.mainloop()
