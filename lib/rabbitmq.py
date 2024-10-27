"""
This module provides a wrapper class, RabbitMQService, for interacting with a RabbitMQ messaging broker. 
The class facilitates the establishment of connections, sending messages to queues, and consuming 
messages from specified queues, simplifying the integration of RabbitMQ into applications.
"""
import pika

class RabbitMQService:

    def __init__(self, host) -> None:
        """
        Initialize the RabbitMQService with the specified host.

        Args:
            host (str): The hostname or IP address of the RabbitMQ server.
        """
        self.host = host
        self.connection = None

    def connect_to_rabbit(self):
        """
        Establish a connection to the RabbitMQ server.

        This method checks if there is an existing connection and attempts to create a new one
        if the current connection is closed.
        """
        if self.connection is None or self.connection.is_closed:
            params = pika.ConnectionParameters(host=self.host)
            self.connection = pika.BlockingConnection(parameters=params)       

    def push_to_queue(self, queue_name, message):
        """
        Push a message to the specified RabbitMQ queue.

        Args:
            queue_name (str): The name of the queue to send the message to.
            message (str): The message to be sent to the queue.

        Raises:
            Exception: If an error occurs while sending the message.
        """
        self.connect_to_rabbit()
        try:
            channel = self.connection.channel()
            channel.queue_declare(queue=queue_name)
            channel.basic_publish(exchange="", routing_key=queue_name, body=message)
        except Exception as ex:
            print(ex)

    def start_consuming(self, queue_name, callback):
        """
        Start consuming messages from the specified RabbitMQ queue.

        Args:
            queue_name (str): The name of the queue to consume messages from.
            callback (function): The callback function to process each received message.
        """
        self.connect_to_rabbit()
        channel = self.connection.channel()
        channel.queue_declare(queue=queue_name)
        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()
