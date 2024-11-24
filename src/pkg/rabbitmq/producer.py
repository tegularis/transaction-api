import json
import pika


class RabbitMqProducer:
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

    def produce(self, data, queue):
        if not self.connection or self.connection.is_closed:
            self.logger.warning(f'RABBITMQ PRODUCER CONNECTION CLOSED, RECONNECTING...')
            self.reconnect()
            self.set_channel(queue)
        self.logger.info(f'RABBITMQ PRODUCER PUBLISHES | exchange: {self.exchange} | queue: {queue}')
        while True:
            try:
                self.channel.basic_publish(exchange=self.exchange, routing_key=queue, body=json.dumps(data))
                break
            except Exception as ex:
                self.logger.sync_warning(f'RABBITMQ CONSUMER RECONNECTING | exception: {ex}')
                self.reconnect()
                self.set_channel(queue)

