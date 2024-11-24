from fastapi import APIRouter, Request, Response


class ClientRouter:

    def __init__(self, controller, middleware, cfg):
        self.controller = controller
        self.middleware = middleware
        self.cfg = cfg
        self.router = APIRouter()

        @self.router.get('/get_me')
        async def get_me(request: Request, response: Response):
            client, message = self.middleware.authenticate(request.headers)
            if not client:
                response.status_code = 401
                return {'ok': False, 'message': message}
            status_code, data = self.controller.get_me(client=client)
            response.status_code = status_code
            return data

        @self.router.post('/set_password')
        async def set_password(request: Request, response: Response):
            client, message = self.middleware.authenticate(request.headers)
            if not client:
                response.status_code = 401
                return {'ok': False, 'message': message}
            body = await request.json()
            if not "data" in body:
                response.status_code = 400
                return {'ok': False, 'message': 'bad request'}
            data = body["data"]
            if not "password" in data:
                response.status_code = 400
                return {'ok': False, 'message': 'bad request'}
            status_code, data = self.controller.set_password(client=client, password=data["password"])
            response.status_code = status_code
            return data
