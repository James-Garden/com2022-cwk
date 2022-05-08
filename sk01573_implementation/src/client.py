import asyncio
import websockets
import asyncio
from queue import Queue

class eventPlanner():
    
    
    def __init__(self):
        self.ip = '127.0.0.1'
        self.port = '1234'
        self.user = 'spyros'
        self.password = 'kalodikis'
        self.sendList = Queue()
        self.rcvList = Queue()
        self.websocket = None
        
        
        asyncio.run(self.startConn())
        
        
    
    async def startConn(self):
        async with websockets.connect(f"ws://{self.ip}:{self.port}") as self.websocket:
            
            #User needs to be authenticated before connection is established
            authenticated = await self.authUser(self.websocket)
            if not authenticated == 'True':
                print("connection failed, user not authenticated")
                self.exit()
            else:
                print("Connection has been established")
                asyncio.create_task(self.sendLoop()) #create loops to send/receive between client/server
                asyncio.create_task(self.rcvLoop())
    
    async def authUser(self, websocket):
        authData = f"P_AUTH;{self.user};{self.password}".encode()
        await websocket.send("Starting User Authentication...")
        await websocket.send(authData)
        ServerResponse = await websocket.recv()
        return (ServerResponse.decode())
    
    
    def readIncoming(self, data):
        data = data.decode()
        command, incoming = data.split(';')
        if command == 'P_EVENT_END':
            print(incoming)
        elif command == 'P_EVENT_EXISTS':
            print(" Can't create an already existing event")
        elif command == "P_NO_EVENT":
            print('There is no event taking place')
        elif command == "P_YOUR_EVENT":
            print('Only invitees can respond to an event')
        elif command == 'P_INVITATION':
            print('Please Accept(Y) or Decline(N) the invitation to: {incoming}')
            input = input('(Y/N)')
            if input == 'Y':
                self.accept()
            if input == 'N':
                self.decline()
        
    async def sendLoop(self):
        try:
            while True:
                
                while not self.sendList.empty():
                    packet = self.sendList.get()
                    await self.websocket.send(packet)
                else:
                    await asyncio.sleep(1)
                    continue
        
        except websockets.ConnectionClosed:
            print("Could not send packet as the connection has been lost")
            

    async def rcvLoop(self):
        try:
            while True:
                packet = await self.websocket.recv()
                self.readIncoming(packet)
            
        except websockets.ConnectionClosed:
            print("Could not receive incoming packets as the connection has been lost")
            
    
    def send(self, msg):
        packet = msg.encode()
        self.sendLoop.append(packet)
    
    def invite(self, msg):
        invitation = 'P_GO_OUT:'+msg
        self.send(invitation)
        
    def accept(self):
        msg = 'P_YES'
        self.send(msg)
    
    def decline(self):
        msg = 'P_NO'
        self.send(msg)
        
    
    async def exit(self):
        await self.websocket.close()
        print('closed connection successfully')
        

if __name__ == "__main__":
    
    event = eventPlanner()
    event.exit()