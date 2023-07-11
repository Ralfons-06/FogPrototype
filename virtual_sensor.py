import zmq
import random
import time
import sys
import config


class VirtualSensor:

    def __init__(self, port, name, coordinates):
        """setup zmq socket
        :param port: port to bind to
        :param socket_type: zmq socket type
        """
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:%s" % port)
        self.name = name
        self.coordinates = coordinates
        self.port = port

    def get_coordinates(self):
        return self.coordinates

    def get_name(self):
        return self.name

    def get_port(self):
        return self.port

    def start_sensor(self, rand_interval, send_interval):
        # generating random data
        # random values
        request_number = 1
        while True:
            virtual_sensor_value = random.randint(rand_interval[0], rand_interval[1])

            message = f"{self.name.upper()} {virtual_sensor_value}"

            # Send random sensor values
            print(f"{self.name.upper()}: Publishing message {request_number} …")
            self.socket.send_string(message)

            time.sleep(send_interval)

            #  Get the reply.
            # message1 = self.socket.recv()
            # print(f"Received reply {request}")
            request_number += 1


if __name__ == "__main__":
    # Create a virtual sensor specified sensor from args
    if len(sys.argv) > 1:
        sensor_key = sys.argv[1]
    else:
        exit("Please specify a sensor to create")

    sensor = VirtualSensor(config.VirtualSensorConfig.SENSORS.get(sensor_key).get("Port"),
                           sensor_key,
                           config.VirtualSensorConfig.SENSORS.get(sensor_key).get("Coordinates"))

    sensor.start_sensor(config.VirtualSensorConfig.SENSORS.get(sensor_key).get("Range"),
                        config.VirtualSensorConfig.SENSORS.get(sensor_key).get("Interval"))

