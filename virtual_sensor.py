import zmq
import random
import time


class VirtualSensor:

    def __init__(self, port, name):
        """setup zmq socket
        :param port: port to bind to
        :param socket_type: zmq socket type
        """
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:%s" % port)
        self.name = name

    def start_sensor(self, message_count, rand_interval, send_interval):
        # generating random data
        # random values
        for request in range(message_count):
            virtual_sensor_value = random.randint(rand_interval[0], rand_interval[1])

            message = f"{self.name.upper()} {virtual_sensor_value}"

            # Send random sensor values
            print(f"{self.name.upper()}: Publishing message {request} …")
            self.socket.send(message.encode('ASCII'))

            time.sleep(send_interval)

            #  Get the reply.
            # message1 = self.socket.recv()
            # print(f"Received reply {request}")
