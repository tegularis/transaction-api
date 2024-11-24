from src.pkg.database import funcs
from src.pkg.database.models import Client
from src.pkg.jwt_manager.main import JwtManager
from src.pkg.logger.main import Logger


class ClientController:
    def __init__(self, jwt_manager: JwtManager, logger: Logger):
        self.jwt_manager = jwt_manager
        self.logger = logger

    @staticmethod
    def get_balance(client_id: int):
        return funcs.get_balance(client_id=client_id)

    @staticmethod
    def get_by_uuid(uuid: str):
        return Client.get(uuid=uuid)

    @staticmethod
    def get_me(client: Client):
        return 200, {
            'ok': True,
            'message': "success",
            'content': {
                "data": {
                    "uuid": client.uuid,
                    "login": client.login,
                    "password": client.password,
                    "balance": funcs.get_balance(client_id=client.id)
                }
            }
        }

    def set_password(self, client: Client, password: str):
        Client.update_field("password", password, id=client.id)
        self.logger.success(f"CLIENT PASSWORD CHANGED | uuid: {client.uuid}")
        return 200, {
            'ok': True,
            'message': "success",
            'content': {}
        }
