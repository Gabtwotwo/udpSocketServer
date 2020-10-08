import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json


clients_lock = threading.Lock()
connected = 0

clients = {}
newPlayer = {}



def connectionLoop(sock):

   while True:
      data, addr = sock.recvfrom(1024)
      
      if addr in clients:
         data = json.loads(data)
         if data['heartbeat'] == "heartbeat":
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]['position'] = data['playerLocation']

      else:
         data = str(data)
         if 'connect' in data:

            JoiningPlayers = {"cmd": 0, "Joining Players" : []}
            for c in clients:
               player = {}
               player['id'] = str(c)
               player['color'] = clients[c]['color']
               player['position'] = clients[c]['position']
               JoiningPlayers['Joining Players'].append(player)

            

            newPlayer['id'] = str(addr)
            newPlayer['init'] = True
            NewPlayer = {"cmd": 0, "newPlayer" : newPlayer}


            clients[addr] = {}
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]['color'] = 0
            clients[addr]['position'] = 0

            message = {"cmd": 0,"player":{"id":str(addr)},"newPlayer": True}

            uniqueID = {"cmd": 3, "uniqueID" : str(addr)}

            m = json.dumps(NewPlayer)
            m2 = json.dumps(JoiningPlayers)
            uniqueIDm = json.dumps(uniqueID)

            sock.sendto(bytes(uniqueIDm, 'utf8'), addr)
            sock.sendto(bytes(m2, 'utf8'), addr)

            for c in clients:
               sock.sendto(bytes(m,'utf8'), c)


def cleanClients(sock):

    while True:
       
        droppedClients = []
       
        for c in list(clients.keys()):
           
            if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
                print('Dropped Client: ', c)


               
                clients_lock.acquire()
               
                del clients[c]
               
                clients_lock.release()
                
                droppedClients.append(str(c))

       
        message = {"cmd": 2, "droppedPlayers": droppedClients}
        m = json.dumps(message, separators=(",", ":"))

        if (len(droppedClients) > 0):
            for c in clients:
                sock.sendto(bytes(m, 'utf8'), (c[0], c[1]))

        time.sleep(1)


def gameLoop(sock):


    pktID = 0  
    while True:
        #print("Boop")
        
        GameState = {"cmd": 1, "pktID": pktID, "players": []}
        clients_lock.acquire()
       
        for c in clients:
            
            player = {}
           
            clients[c]['color'] = {"R": random.random(), "G": random.random(), "B": random.random(), }
            
            player['id'] = str(c)
            player['color'] = clients[c]['color']
            player['position'] = clients[c]['position']
            GameState['players'].append(player)
        s = json.dumps(GameState, separators=(",", ":"))
        print(s)
        for c in clients:
            sock.sendto(bytes(s, 'utf8'), (c[0], c[1]))
        clients_lock.release()
        if (len(clients) > 0):
            pktID = pktID + 1
        time.sleep(0.3333333)





def main():
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))
    start_new_thread(gameLoop, (s, ))
    start_new_thread(connectionLoop, (s, ))
    start_new_thread(cleanClients, (s, ))
   
    while True:
        time.sleep(1)
if __name__ == '__main__':
    main()