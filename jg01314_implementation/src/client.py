import socket
import threading
import tkinter as tk
from queue import Queue

# Defining constants
SERVER = ('127.0.0.1', 1234)  # Server hostname and port
USER = "james_g"              # User login name

# Defining global variables
invitation_received = False
server_log = Queue()


# Creating the client GUI
class Interface(tk.Tk):
    # Constructor
    def __init__(self, conn):
        super().__init__()
        # Displayed log
        self.log = Queue()
        # Server connection
        self.sock = conn
        # Window title
        self.title("Event Planning Protocol - Client")
        # Welcome message
        self.greeting = tk.Label(text=f"Welcome, {USER}", )
        # Text entry box for sending an invitation
        self.send_inv_entry = tk.Entry(width=50, justify='center')
        # Button to send invitation
        self.send_inv_button = tk.Button(width=15, height=3, command=self.send_invitation, text="Send Invitation")
        # Box containing message from a currently active invitation
        self.active_inv_text = tk.Entry(width=50, justify='center')
        self.active_inv_text.insert('end', "No Active Invitation")
        self.active_inv_text.config(state='disabled')
        # Buttons frame
        self.button_frame = tk.Frame()
        # Button to accept an invitation
        self.yes_button = tk.Button(self.button_frame, width=8, height=2, command=self.accept_invite, text="Yes")
        # Button to reject an invitation
        self.no_button = tk.Button(self.button_frame, width=8, height=2, command=self.reject_invite, text="No")
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
        self.after(0, self.refresh)  # Start refreshing

    # Send an invitation to the server
    def send_invitation(self):
        msg = "Invitation:"+self.send_inv_entry.get()
        self.sock.sendall(msg.encode())

    # Accept/Reject an invitation from another user
    def accept_invite(self):
        pass

    def reject_invite(self):
        pass

    # Check for messages from the server
    def refresh(self):
        global server_log
        if server_log.empty():  # If there is nothing to be read from the log of server messages
            self.after(10, self.refresh)  # Wait 0.5s then check again
        else:  # If there are messages waiting to be read
            data = server_log.get()
            self._update_log(data)  # Update the log section of the client
            self._check_for_invite(data)  # Check if an invitation has been received

            self.after(10, self.refresh)  # Wait 0.01s then check again

    def _update_log(self, data):
        msg = "[SERVER] " + data.decode() + "\n"
        if self.log.qsize() == 10:  # If the output area of the client is full
            self.log_text.delete('1.0', tk.END)  # Clear the output area
            self.log.get()  # Remove the oldest message from the queue
            self.log.put(msg)
            for i in range(0, 10):
                pos = str(i) + '.0'
                self.log_text.insert(pos, self.log.queue[i])
        else:
            pos = str(self.log.qsize() + 1) + '.0'
            self.log_text.insert(pos, msg)

    def _check_for_invite(self, data):
        data = data.decode().split(":")
        msg_type, msg = data[0], ''.join(data[1:])
        if msg_type == "Invitation":
            self.active_inv_text.config(state='normal')
            self.active_inv_text.delete('0', tk.END)
            self.active_inv_text.insert('end', msg)
            self.active_inv_text.config(state='readonly')


# Thread which just awaits data from server
class ReceiveThread(threading.Thread):
    def __init__(self, conn):
        super().__init__()
        self.sock = conn

    def run(self):
        while True:
            data = self.sock.recv(1024)
            print("Received data:", data.decode())
            server_log.put(data)


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create the socket
    try:
        sock.connect(SERVER)  # Connect to the server
        sock.send(b"")
        recv_thread = ReceiveThread(sock)  # Create a thread for receiving packets
        recv_thread.daemon = True  # The receiving thread should close when the program does, else it would loop forever
        recv_thread.start()  # Listen for packets from the server

        root = Interface(sock)  # Create the GUI
        root.mainloop()  # Launch the GUI

        sock.close()  # Close the connection to the server when the user closes the tkinter window
    except TimeoutError:
        print(f"Error: Connection to server at {SERVER[0]}:{SERVER[1]} timed out")
        input("Press ENTER to quit")
    except InterruptedError:
        print("Error: Connection to server interrupted")
        input("Press ENTER to quit")
