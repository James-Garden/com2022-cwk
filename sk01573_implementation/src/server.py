import websockets
import asyncio


class server():
    
    def __init__(self):
        
        self.ip = '0.0.0.0'
        self.port = '5678'
        self.allowed = {
            'spyros' : 'kalodikis',
            'markos' : 'doufos',
            'james' : 'titman',
            'james' : 'garden'}
        self.auth = False
        self.clients = {}
        self.websocket = None
        self.invitation = None
        self.responses = []
        
        
    
    async def handler(self, websocket, authorise, eventRequest, response):
        while True:
            if not self.auth:
                self.authorise(self, websocket)
            
            else:
                self.eventRequest(self, websocket)
                self.response(self)
    
    
    async def authorise(self, websocket):
        
        while True:
            if not self.auth:
                print('Starting client authorisation')
                incoming = websocket.recv()
                incoming = incoming.decode()
                incoming = incoming.split(';')
                
                if (incoming[0] == 'P_AUTH') and (incoming[1] in self.allowed.keys()) and (self.allowed[incoming[1]] == incoming[2]):
                    self.auth = True
                    await websocket.send('True'.encode())
                    self.clients[websocket] = (incoming[1], None)
                    self.websocket = websocket
                    print("client has been authorised")
                    
                    
                    
    async def eventRequest(self, websocket):
        self.websocket = websocket
        packet = await self.websocket.recv()
        if self.invitation is None:
            if packet is not None:
                msg = packet.split(';')
                if msg[0] == 'P_GO_OUT':
                    self.invitation = websocket
                    msg[0] = 'P_INVITATION'
                    msg = ';'.join(msg)
                    
                    
                    
                    for client in self.clients.keys():
                        if client != self.invitation:
                            await client.send(msg.encode())
                
                elif msg[0] == 'P_YES':
                    await websocket.send('P_NO_EVENT; There are no events to respond to'.encode())
                
                elif msg[0] == 'P_NO':
                    await websocket.send('P_NO_EVENT; There are no events to respond to'.encode())
                
                
            
            elif packet is not None:
                msg = packet.split(';')
                
                if msg[0] == 'P_GO_OUT':
                    await websocket.send('P_EVENT_EXISTS; An event is already in progress'.encode())
                
                elif (msg[0] == 'P_YES') and websocket == self.invitation:
                    await websocket.send('P_YOUR_EVENT; You cannot respond to your own proposed event'.encode())
                
                elif (msg[0] == 'P_NO') and websocket == self.invitation:
                    await websocket.send('P_YOUR_EVENT; You cannot respond to your own proposed event'.encode())
                    
                elif msg[0] == 'P_YES':
                    self.clients[websocket][1] = 'Yes'
                
                elif msg[0] == 'P_NO':
                    self.clients[websocket][1] = 'No'
                
                
    async def response(self):
        
        responded = True
        
        for client in self.clients.keys():
            if self.clients[client][1] is None:
                responsed = False
        
        
        if responsed:
            for client in self.clients.keys():
                responses.append(f"User {self.cleints[client][0]}: {self.clients[client][1]}")
            
            respond = 'P_EVENT_END;' +  '/n'.join(responses)
            await self.invitation.send(respond.encode())
            self.invitation = None
                
    
    def start(self):
        
        start_server = websockets.serve(self.handler, self.ip, self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
        
    def exit(self):
        self.websocket.close()
        del self
                
      
server = server()
server.start()
                