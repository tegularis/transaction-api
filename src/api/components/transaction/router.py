from typing import Union, Optional

from fastapi import APIRouter, Request, Response

from src.pkg.rabbitmq.consumer import RabbitMqConsumer


class TransactionRouter:
    def __init__(self, controller, middleware, cfg, logger):
        self.controller = controller
        self.middleware = middleware
        self.cfg = cfg
        self.router = APIRouter()
        self.consumer = RabbitMqConsumer(cfg=cfg, exchange="transactions", exchange_type="topic", logger=logger)
        self.consumer.consume(self.controller.process, queue="processing")

        @self.router.post('/send')
        async def send(request: Request, response: Response):
            client, message = self.middleware.authenticate(request.headers)
            if not client:
                response.status_code = 401
                return {'ok': False, 'message': message}
            body = await request.json()
            if not "data" in body:
                response.status_code = 400
                return {'ok': False, 'message': 'bad request'}
            data = body["data"]
            if not ("receiver_uuid" in data and "amount" in data and "status" in data):
                response.status_code = 400
                return {'ok': False, 'message': 'bad request'}
            status_code, data = self.controller.send(
                sender=client, receiver_uuid=data["receiver_uuid"], amount=data["amount"], status=data["status"])
            response.status_code = status_code
            return data

        @self.router.get('/history')
        async def history(request: Request, response: Response,
                          limit: Optional[int] = None, offset: Optional[int] = None,
                          status: Optional[str] = None, side: Optional[str] = None):
            client, message = self.middleware.authenticate(request.headers)
            if not client:
                response.status_code = 401
                return {'ok': False, 'message': message}
            if status and status not in ["completed", "cancelled", "revised"]:
                response.status_code = 400
                return {'ok': False, 'message': "invalid status"}
            if side and side not in ["receiver", "sender"]:
                response.status_code = 400
                return {'ok': False, 'message': "invalid side"}
            status_code, data = self.controller.get_all(
                client=client, side=side, limit=limit, offset=offset, status=status)
            response.status_code = status_code
            return data
