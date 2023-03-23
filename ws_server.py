import aiohttp
from aiohttp import web
# from aiohttp_session import get_session

# https://github.com/steelkiwi/aiohttp_test_chat/tree/2a11520e811ccdd47a6c9a6422dd2c22b0ea7a40
# https://steelkiwi.com/blog/an-example-of-a-simple-chat-written-in-aiohttp/
app = web.Application()
app['websockets'] = []
users_list = []
user_number = 0

class WebSocket(web.View):
    async def get(self):
        global user_number

        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        # session = await get_session(self.request)
        # print(session)
        login = f"user {user_number}"
        users_list.append(login)
        user_number += 1

        print(f'user {login} connected')
        for _ws in self.request.app['websockets']:
            await _ws.send_str(f"{login} joined")
        self.request.app['websockets'].append(ws)

        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                if msg.data == 'CLOSE':
                    await ws.close()
                else:
                    for _ws in self.request.app['websockets']:
                        await _ws.send_str(f"{login}:: {msg.data}")
            if msg.type == web.WSMsgType.ERROR:
                print(f"ws connection closed with exception: {ws.exception()}")
        self.request.app['websockets'].remove(ws)
        for _ws in self.request.app['websockets']:
            await _ws.send_str(f"{login} disconnected")
        users_list.remove(login)
        user_number -= 1
        print('websocket closed connection')

        return ws

app.add_routes([web.get('/ws', WebSocket)])
web.run_app(app)

