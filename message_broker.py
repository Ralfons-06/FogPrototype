import zmq
import datetime
import jwt

class MessageBroker:

    def __init__(self, port, socket_type):
        """setup zmq socket
        :param port: port to bind to
        :param socket_type: zmq socket type
        """
        self.context = zmq.Context()
        self.socket = self.context.socket(socket_type)
        self.socket.bind("tcp://*:%s" % port)
        self.message_queue = {}
        

    def send(self, topic, message):
        self.socket.send_string("%s %s" % (topic, message))

    
    def check_hearbeat(self):
        # "Subscribe" to heartbeat of devices
        pass

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