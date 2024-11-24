import uvicorn
from fastapi import FastAPI
from src.api.components.client.controller import ClientController
from src.api.components.client.router import ClientRouter
from src.api.components.middleware.main import Middleware
from src.api.components.transaction.controller import TransactionController
from src.api.components.transaction.router import TransactionRouter
from src.pkg.jwt_manager.main import JwtManager


class App:
    def __init__(self, cfg, logger):
        self.cfg = cfg
        jwt_manager = JwtManager(cfg)
        middleware = Middleware(jwt_manager=jwt_manager, logger=logger)

        client_controller = ClientController(
            jwt_manager=jwt_manager, logger=logger)
        transaction_controller = TransactionController(
            cfg=cfg, client_controller=client_controller, jwt_manager=jwt_manager, logger=logger)

        self.app = FastAPI()
        self.app.include_router(
            ClientRouter(
                controller=client_controller,
                cfg=cfg,
                middleware=middleware
            ).router, prefix="/client")
        self.app.include_router(
            TransactionRouter(
                controller=transaction_controller,
                cfg=cfg,
                middleware=middleware,
                logger=logger
            ).router, prefix="/transaction")

    def run(self):
        uvicorn.run(self.app, host=self.cfg["app"]["host"], port=self.cfg["app"]["port"])