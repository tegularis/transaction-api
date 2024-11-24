from threading import Thread
from typing import Callable, Any
import pika


class RabbitMqConsumer:
    def __init__(self, cfg, exchange, exchange_type, logger):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=cfg['rabbitMq']['host'],
                                      port=cfg['rabbitMq']['port'],
                                      credentials=pika.PlainCredentials(
                                          username=cfg['rabbitMq']['username'],
                                          password=cfg['rabbitMq']['password']),
                                      heartbeat=600,
                                      blocked_connection_timeout=600))

        self.cfg = cfg
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.logger = logger
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=exchange, durable=True, exchange_type=exchange_type)

    def reconnect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.cfg['rabbitMq']['host'],
                                      port=self.cfg['rabbitMq']['port'],
                                      credentials=pika.PlainCredentials(
                                          username=self.cfg['rabbitMq']['username'],
                                          password=self.cfg['rabbitMq']['password']),
                                      heartbeat=600,
                                      blocked_connection_timeout=600))

    def set_channel(self, queue):
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange, durable=True, exchange_type=self.exchange_type)
        self.channel.queue_declare(queue=queue, durable=True)
        self.channel.queue_bind(exchange=self.exchange, queue=queue, routing_key=queue)

    def consume(self, callback_func: Callable[[str, str, str, bytes], Any], queue: str):
        def consumer_wrapper():
            while True:
                try:
                    self.set_channel(queue=queue)
                    self.logger.info(f'RABBITMQ CONSUMER STARTED | queue: {queue}')
                    self.channel.basic_consume(queue=queue, on_message_callback=callback_func, auto_ack=True)
                    self.channel.start_consuming()
                except Exception as ex:
                    self.logger.warning(f'RABBITMQ CONSUMER RECONNECTING | exception: {ex}')
                    self.reconnect()

        thread = Thread(target=consumer_wrapper)
        thread.start()
        return
