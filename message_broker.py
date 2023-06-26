import zmq
import datetime
import jwt
import time
import pandas as pd
from multiprocessing import Process


class MessageBroker:

    def __init__(self, port, socket_type):
        """setup zmq socket
        :param port: port to bind to
        :param socket_type: zmq socket type
        """
        self.context = zmq.Context()

        # Init sensor socket
        self.sensor_socket = self.context.socket(zmq.SUB)
        # eventually use one port for each sensor
        self.sensor_socket.bind("tcp://*:%s" % port)
        self.message_queue = pd.DataFrame(columns=["message", "timestamp", "consumed_by"])
        self.topic = [b"temperature", b"humidity", b"air quality", b"magnitude"]
        for topic in self.topic:
            self.sensor_socket.setsockopt(zmq.SUBSCRIBE, topic)

        # Init cloud socket
        self.cloud_socket = self.context.socket(zmq.REQ)
        self.cloud_socket.connect("tcp://localhost:5555")

        self.cloud_components = {}
        self.dead_components = []

    def add_cloud_component(self, component):
        self.cloud_components[component] = None

    def remove_cloud_component(self, component):
        self.cloud_components.pop(component)

    def add_topic(self, topic):
        """
        Add topic/sensor to subscription
        Args:
            topic: name of sensor to subscribe to
        Returns:

        """
        self.sensor_socket.setsockopt(zmq.SUBSCRIBE, topic)

    def remove_topic(self, topic):
        """
        Remove topic/sensor from subscription
        Args:
            topic: name of sensor to unsubscribe from

        Returns:

        """
        self.sensor_socket.setsockopt(zmq.UNSUBSCRIBE, topic)

    def start_receiver(self):
        """
        Receive messages from sensors and add them to queue

        Returns:

        """
        while True:
            #  Wait for next request from client
            message = self.sensor_socket.recv()
            print(f"Received request: {message}")

            self.message_queue.append({"message": message, "timestamp": time.time(), "consumed_by": []})

    def start_sender(self):
        """
        Send messages from queue to cloud component

        Returns:
        """
        while True:
            if len(self.message_queue) > 0:
                message = self.message_queue[0]
                self.cloud_socket.send(message)

    def confirm_received(self):
        """
        Confirm that message was received by cloud component and marks it in the queue / delete if
        all cloud components received it

        Returns:

        """
        while True:
            message = self.cloud_socket.recv()
            device_id = message[1]
            print(f"Message: {message} received by {device_id}")
            # add device_id to consumed_by list
            self.message_queue.loc[self.message_queue["message"] == message, "consumed_by"].append(device_id)
            # check if all cloud components received the message and delete it from queue if so
            if len(self.message_queue.loc[self.message_queue["message"] == message, "consumed_by"]) == len(self.cloud_components):
                self.message_queue.drop(self.message_queue.loc[self.message_queue["message"] == message].index)

    def check_hearbeat(self):
        """
        Check if heartbeat of component is still active
        Returns:

        """
        heartbeat_notify_socket = self.context.socket(zmq.PUB)
        heartbeat_notify_socket.bind("tcp://*:%s" % 5556)
        heartbeat_notify_socket.send_string("heartbeat")

        heartbeat_reply_socket = self.context.socket(zmq.SUB)
        heartbeat_reply_socket.connect("tcp://localhost:5556")
        heartbeat_reply_socket.setsockopt(zmq.SUBSCRIBE, b"heartbeat")

        start_time = time.time()
        timer = 0
        while timer < 25:
            message = heartbeat_reply_socket.recv().split()
            device_id = message[1]
            if device_id in self.cloud_components:
                self.cloud_components[device_id].last_heartbeat = time.time()
            timer = time.time() - start_time

        for component in self.cloud_components:
            if time.time() - component.last_heartbeat > 325:
                print(f"Component {component} shows no heartbeat since more than 5 minutes.")
                self.dead_components.append(component)
                self.cloud_components.pop(component)

    def receive(self):
        pass

    def check_received(self):
        pass

    def retry_send(self):
        pass

    # JWT configuration function: https://cloud.google.com/iot/docs/how-tos/credentials/jwts?hl=de#iot-core-jwt-nodejs
    def create_jwt(self, project_id, private_key_file, algorithm):
        """Creates a JWT (https://jwt.io) to establish an MQTT connection with Cloud component.
        Args:
        project_id: The cloud project ID this device belongs to
        private_key_file: A path to a file containing either an RSA256 or
                ES256 private key.
        algorithm: The encryption algorithm to use. Either 'RS256' or 'ES256'
        Returns:
            A JWT generated from the given project_id and private key, which
            expires in 20 minutes. After 20 minutes, your client will be
            disconnected, and a new JWT will have to be generated.
        Raises:
            ValueError: If the private_key_file does not contain a known key.
        """

        token = {
            # The time that the token was issued at
            "iat": datetime.datetime.now(tz=datetime.timezone.utc),
            # The time the token expires.
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=20),
            # The audience field should always be set to the GCP project id.
            "aud": project_id,
        }

        # Read the private key file.
        with open(private_key_file) as f:
            private_key = f.read()

        print(
            "Creating JWT using {} from private key file {}".format(
                algorithm, private_key_file
            )
        )

        return jwt.encode(token, private_key, algorithm=algorithm)
