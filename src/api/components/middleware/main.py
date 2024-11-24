from typing import Union
from src.pkg.database.models import Client
from src.pkg.jwt_manager.main import JwtManager
from src.pkg.clock.main import get_seconds_since_epoch
from src.pkg.logger.main import Logger


class Middleware:
    def __init__(self, jwt_manager: JwtManager, logger: Logger):
        self.jwt_manager = jwt_manager
        self.logger = logger

    def authenticate(self, headers: dict) -> (Union[dict, None], str):
        if not "AUTH-TOKEN" in headers:
            return None, "authentication failed"
        payload = self.jwt_manager.decode(headers["AUTH-TOKEN"])
        if not payload:
            return None, "invalid token"
        if payload["expiration_time"] < get_seconds_since_epoch():
            return None, "token expired"
        client = Client()
        client.id = payload["client"]["id"]
        client.uuid = payload["client"]["uuid"]
        client.login = payload["client"]["login"]
        client.password = payload["client"]["password"]
        self.logger.info(f"CLIENT AUTHENTICATED | uuid: {client.uuid}")
        return client, "authenticated"
