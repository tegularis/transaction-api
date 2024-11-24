import json
from typing import Union

from Tools.demo.mcast import receiver

from src.api.components.client.controller import ClientController
from src.pkg.database import funcs
from src.pkg.database.models import Client, Transaction
from src.pkg.jwt_manager.main import JwtManager
from src.pkg.logger.main import Logger
from src.pkg.rabbitmq.producer import RabbitMqProducer


class TransactionController:
    def __init__(self, cfg, client_controller: ClientController, jwt_manager: JwtManager, logger: Logger):
        self.client_controller = client_controller
        self.jwt_manager = jwt_manager
        self.logger = logger
        self.producer = RabbitMqProducer(cfg=cfg, exchange="transactions", exchange_type="topic", logger=logger)

    def process(self, _ch: str, _method: str, _properties: str, body: bytes):
        data = json.loads(body)
        transaction = Transaction.get(uuid=data["uuid"])
        balance = self.client_controller.get_balance(transaction.sender_id)
        if transaction.amount > balance:
            Transaction.update_field("status", "cancelled", id=transaction.id)
            self.logger.info(f"TRANSACTION CANCELLED (INSUFFICIENT BALANCE) | uuid: {data['uuid']}")
            return
        Transaction.update_field("status", "completed", id=transaction.id)
        self.logger.success(f"TRANSACTION COMPLETED | uuid: {data['uuid']}")
        return

    def send(self, sender: Client, receiver_uuid: str, amount):
        try:
            amount = float(amount)
        except:
            return 400, {'ok': False, 'message': 'bad request'}
        if amount <= 0:
            return 400, {'ok': False, 'message': 'bad request'}
        balance = self.client_controller.get_balance(sender.id)
        if amount > balance:
            return 400, {'ok': False, 'message': 'insufficient balance'}
        receiver = self.client_controller.get_by_uuid(uuid=receiver_uuid)
        if not receiver:
            return 404, {'ok': False, 'message': 'receiver does not exist'}
        data = funcs.create_transaction(
            amount=amount, receiver_uuid=receiver_uuid, sender_id=sender.id, status="revised")
        if not data:
            return 404, {'ok': False, 'message': 'unable to create transaction'}
        self.producer.produce(
            data=json.dumps(
                {
                    "uuid": data["uuid"]
                }
            ),
            queue="processing"
        )
        self.logger.info(f"TRANSACTION SENT TO PROCESSING QUEUE | uuid: {data['uuid']}")
        return 202, {
            'ok': True,
            'message': "processing transaction",
            'content': {
                "data": {
                    "uuid": data["uuid"]
                }
            }
        }

    def get_history(self, client: Client, side: str,
                    limit: Union[int, None], offset: Union[int, None], status: Union[str, None]):
        match side:
            case "receiver":
                transactions = Transaction.get_all(receiver_id=client.id, status=status, limit=limit, offset=offset)
            case "sender":
                transactions = Transaction.get_all(sender_id=client.id, status=status, limit=limit, offset=offset)
            case _:
                transactions = Transaction.get_all(
                    sender_id=client.id, status=status, limit=limit, offset=offset
                ) + Transaction.get_all(
                    receiver_id=client.id, status=status, limit=limit, offset=offset)
        self.logger.info(f"CLIENT TRANSACTIONS HISTORY FETCHED | uuid: {client.uuid}")
        return 200, {
            'ok': True,
            'message': "success",
            'content': {
                "data": {
                    "list": transactions
                }
            }
        }
