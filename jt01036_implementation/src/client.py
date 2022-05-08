import asyncio
from asyncio.windows_events import NULL
import websockets

class EventProtocol():

    def __init__(self):
        self.serverip = "localhost"
        self.serverport = 8765
        self.username = "james_t"
        self.password = "titman"
        self.websocket = None
        self.sendlist = []
        self.receivelist = []

        asyncio.run(self.connect())

    async def authenticate(self, websocket):
        try:
            details = f"P_AUTH;{self.username};{self.password}".encode()
            await websocket.send(details)
            reply = await websocket.recv()
            return bool(reply.decode())
        except OSError:
            print("Authentication failed")
            self.exit()

    async def connect(self):
        try:
            print("Trying to connect")
            async with websockets.connect(f"ws://{self.serverip}:{self.serverport}") as self.websocket:
                if self.authenticate(self.websocket):
                    asyncio.create_task(self.sendloop())
                    asyncio.create_task(self.receiveloop())
                    print("Connected Succesfully")

        except OSError:
            print("Connection failed")
            self.exit()

    def readpacket(self, data):
        data = data.decode()
        protocolcode, protocoldata = data.split(";")
        if protocolcode == "P_INVITATION":
            print(f"/nYou have received an invitation:/n/n{protocoldata}")
            while not(reply == "Y" or reply == "N"):
                reply =input("/nWill you go(Y/N)?")
            if reply == "Y":
                self.accept()
            if reply == "N":
                self.reject()
        elif protocolcode == "P_EVENT_EXISTS":
            print("ERROR: Event already exists")
        elif protocolcode == "P_NO_EVENT":
            print("ERROR: No current events")
        elif protocolcode == "P_YOUR_EVENT":
            print("ERROR: Can not reply to own invite")
        elif protocolcode == "P_EVENT_END":
            print(protocoldata)

    async def sendloop(self):
        try:
            while True:
                if self.sendlist:
                    await self.websocket.send(self.sendlist.pop(0))
                else:
                    await asyncio.sleep(1)
                    continue

        except websockets.ConnectionClosed:
            print("Error sending packet as connection closed unexpectedly")

    async def receiveloop(self):
        try:
            while True:
                packet = await self.websocket.recv()
                self.readpacket(packet)
        except websockets.ConnectionClosed:
            print("Error receiving packets as connection closed unexpectedly")

    def send(self, packet):
        self.sendlist.append(packet.encode())

    def invite(self, msg):
        data = "P_GO_OUT;"+msg
        self.send(data)

    def accept(self):
        data = "P_YES;True"
        self.send(data)

    def reject(self):
        data = "P_NO;False"
        self.send(data)

    def exit(self):
        try:
            self.websocket.close()
        except AttributeError:
            print("ERROR: Could not make connection")
        del self
        print("Exited Successfully")

if __name__ == "__main__":
    e = EventProtocol()
    e.exit()

