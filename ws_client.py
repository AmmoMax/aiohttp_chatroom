import asyncio
import os

import aioconsole
import aiohttp
from aiohttp import ClientWebSocketResponse

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8080))

URL = f'http://{HOST}:{PORT}/ws'


async def subscribe_to_message(websocket: ClientWebSocketResponse):
    async for msg in websocket:
        print(f"received msg: {msg}")


async def ping(websocket: ClientWebSocketResponse):
    while True:
        await websocket.ping()
        await asyncio.sleep(60)


async def send_input_message(websocket: ClientWebSocketResponse):
    while True:
        message = await aioconsole.ainput('<<<')
        if message == 'exit':
            await websocket.close()
        else:
            await websocket.send_str(message)

async def main():
    session = aiohttp.ClientSession()
    async with session.ws_connect(URL) as ws:
        read_message_task = asyncio.create_task(subscribe_to_message(websocket=ws))
        ping_task = asyncio.create_task(ping(websocket=ws))
        send_input_task = asyncio.create_task(send_input_message(websocket=ws))

        done, pending = await asyncio.wait([read_message_task,
                                            ping_task,
                                            send_input_task], return_when=asyncio.FIRST_COMPLETED)
        if not ws.closed:
            await ws.close()

        for task in pending:
            task.cancel()


# async def prompt_and_send(ws):
#     # todo: blocking operation! need to fix
#     # new_msg_to_send = input('Type a message to send to the server: ')
#     new_msg_to_send = await aioconsole.ainput('Type a message to send to the server: ')
#     if new_msg_to_send == 'exit':
#         print('Exiting!')
#         raise SystemExit(0)
#     await ws.send_str(new_msg_to_send)

asyncio.run(main())