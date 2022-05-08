import asyncio
import websockets

class server():
    def __init__(self):
        self.clientip = "localhost"
        self.clientport = "6543"
        self.websocket = None
        self.authdict = {
        "james_t": "titman",
        "james_g": "garden",
        "markos": "doufos",
        "spyros": "kalodikis"}
        self.authorised = False
        self.currentinvite = None
        self.clients = {}

    

    def exit(self):
        try:
            self.websocket.close()
        except IOError:
            print("No connection")
        del self

    async def handler(self, websocket):
        print("server ran")
        while True:
            if not self.authorised:
                auth = websocket.recv()
                auth = auth.decode()
                auth = auth.split(";")
                if auth[0] == "P_AUTH":
                    if auth[1] in self.authdict.keys():
                        if self.authdict[auth[1]] == auth[2]:
                            self.autharised = True
                            await websocket.send("True".encode())
                            self.clients[websocket] = (auth[1], None)
                            self.websocket = websocket

            else:
                self.websocket = websocket
                incoming = await self.websocket.recv()
                if (self.currentinvite is None) and (incoming is not None):
                    data = incoming.split(";")
                    if data[0] == "P_GO_OUT":
                        self.currentinvite = websocket
                        data[0] = "P_INVITATION"
                        data = ";".join(data)
                        for client in self.clients.keys():
                            if client != self.currentinvite:
                                await client.send(data.encode())

                    elif data[0] == "P_YES" or data[0] == "P_NO":
                        await websocket.send("P_NO_EVENT;There are currently no events".encode())
                
                elif incoming is not None:
                    data = incoming.split(";")
                    if data[0] == "P_GO_OUT":
                        await websocket.send("P_EVENT_EXISTS;Event already in progress".encode())
                    elif (data[0] == "P_YES" or data[0] == "P_NO") and websocket == self.currentinvite:
                        await websocket.send("P_YOUR_EVENT;Trying to reply to own event".encode())
                    elif data[0] == "P_YES":
                        self.clients[websocket][1] = "Yes"
                    elif data[0] == "P_NO":
                        self.clients[websocket][1] = "No"
            
                replied = True
                for client in self.clients.keys():
                    if self.clients[client][1] is None:
                        replied = False
            
                if replied:
                    replies = []
                    for client in self.clients.keys():
                        replies.append(f"User {self.clients[client][0]}: {self.clients[client][1]}")
                    send = "P_EVENT_END;"+"/n".join(replies)
                    await self.currentinvite.send(send.encode())
                    self.currentinvite = None
    
    def start(self):
        startserver = websockets.serve(self.handler, self.clientip, self.clientport)
       
        asyncio.get_event_loop().run_until_complete(startserver)
        asyncio.get_event_loop().run_forever()

s = server()
s.start()
   