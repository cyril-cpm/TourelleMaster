from Settingator import *
from PySerialCommunicator import *
from TKDisplay import *
from PySimpleGUIDisplay import *

import asyncio
import websockets
import threading

connected_clients = set()
message_queue = asyncio.Queue()

async def handler(websocket, path=None):
    connected_clients.add(websocket)
    print("Client connect")
    try:
        async for message in websocket:
            print(f"Message reçu : {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Client déconnecté")
    finally:
        connected_clients.remove(websocket)

async def broadcaster():
    while True:
        msg = await message_queue.get()
        for client in connected_clients:
            try:
                await client.send(msg)
            except:
                pass

async def serveur():
    async with websockets.serve(handler, "localhost", 8765):
        print("Serveur lancé sur ws://localhost:8765")
        await asyncio.Future()  # bloque indéfiniment

def envoyer_message_à_tous(msg: str):
    # Appelé depuis le thread principal
    loop.call_soon_threadsafe(message_queue.put_nowait, msg)

def lancer_serveur():
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


    # Lancer la tâche de diffusion
    loop.create_task(broadcaster())
    # Lancer le serveur
    loop.run_until_complete(serveur())

    loop.run_forever()

# Démarrer le serveur WebSocket dans un thread à part
threading.Thread(target=lancer_serveur, daemon=True).start()
BUZZ_BUTTON = 5

def buzzButton(slaveID:int):
    envoyer_message_à_tous("pulse")


if __name__ == "__main__":
    com = SerialCTR(PySimpleGUIDisplay.SelectCOMPort(SerialCTR))

    display = TKDisplay()

    STR = Settingator(com, display)

    STR.BridgeStartInitBroadcasted()
    STR.AddNotifCallback(BUZZ_BUTTON, buzzButton)

# Exemple : appeler cette fonction depuis le thread principal
while True:
    STR.Update()