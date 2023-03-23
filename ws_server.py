import aiohttp
from aiohttp import web
# from aiohttp_session import get_session

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

