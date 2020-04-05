from aiohttp import web
import json


async def handle(request):
    response_obj = {'status': 'success'}
    return web.Response(text=json.dumps(response_obj))




async def new_user(request):
    try:
        user = request.query['name']
        print("Creating new user with name: ", user)

        response_obj = {'status': 'success','message':'user succesfully created'}
        return web.Response(text=json.dumps(response_obj), status=200)

    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.Response(text=json.dumps(response_obj), status=500)



app = web.Application()
app.router.add_get('/', handle)
app.router.add_post('/user', new_user)


web.run_app(app)
