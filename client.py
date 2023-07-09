import zmq
import random
import time
from collections import deque
from virtual_sensor import VirtualSensor
import config
from threading import Thread


class MessageBroker:
    def __init__(self):
        # Create ZeroMQ context & socket of type REQ
        self.context = zmq.Context()
        self.server_socket = self.context.socket(zmq.REQ)

        # Connect socket to server
        self.server_socket.connect("tcp://localhost:5555")

        # Create a queue to store data for later transmission
        self.data_queue = deque()
        self.failed_data_queue = deque()
        self.i = 0

        # init sensor ports
        self.sensor_socket = self.context.socket(zmq.SUB)
        self.sensor_socket.subscribe(b"")
        self.init_sensors()

    def init_sensors(self):
        """
        Initialise the sensors by connecting a socket of the client to the configured ports of the sensors
        Returns:

        """
        print("Initialising sensors...")
        sensor_ports = {}
        current_conf = config.VirtualSensorConfig.SENSORS
        for sensor in current_conf.keys():
            sensor_ports[sensor] = current_conf.get(sensor).get("Port")
            print(f"Configuration: Sensor {sensor.capitalize()} on Port {current_conf.get(sensor).get('Port')}")

        for sensor in sensor_ports.items():
            self.sensor_socket.connect(f"tcp://localhost:%s" % sensor[1])
            print(f"Successfully connected to sensor {sensor[0]} on port {sensor[1]}")

    def start(self):
        """
        Start the client processes for receiving and sending data

        Returns:

        """

        # TODO: multithread receiving and sending so that message broker can receive and send at the same time
        rec_thread = None
        send_thread = None

        # Listen to sensor ports for incoming data
        # Send data to the server
        # TODO: multihreading
        try:
            rec_thread = Thread(target=self.receive_data_from_sens)
            send_thread = Thread(target=self.send_data_to_server)

            send_thread.start()
            rec_thread.start()


        except KeyboardInterrupt:

            # Cleanly exit the program on Ctrl+C
            self.server_socket.close()
            self.sensor_socket.close()
            self.context.term()

    def receive_data_from_sens(self):
        """
        Receive data from sensors
        Returns:

        """
        while True:
            try:
                current_message = self.sensor_socket.recv_string()
                print(current_message.capitalize())
                self.data_queue.append(current_message)
            except zmq.ZMQError as e:
                print("Error occurred:", e)
            time.sleep(1)

    def process_server_response(self, response):
        """
        Process the server's response
        Args:
            response:

        Returns:

        """
        # Replace this with your processing logic for the server's response
        print("Processed server response:", response)

    def send_data_to_server(self):
        """
        Send data to the server starting with the data that failed to send to the server
        if the server is not available, store the data in an extra queue for priority processing when the server is
        available again

        Returns:

        """
        # TODO: Process Server Response
        while True:
            try:
                # Check if there is any failed data to send
                if self.failed_data_queue:
                    print("Sending failed data...")
                    while self.failed_data_queue:
                        # TODO: Check if data should be send one after one or in a batch
                        self.server_socket.send(self.failed_data_queue.popleft())
                        response = self.server_socket.recv().decode()
                        print("Received response from server:", response)
                    print("All failed data sent successfully")
                elif self.data_queue:
                    self.server_socket.send_string(self.data_queue.popleft())
                    response = self.server_socket.recv().decode()
                    print("Received response from server:", response)

            except zmq.ZMQError as e:
                print("Error occurred:", e)
                # Handle disconnection or crash here, store data in the queue
                self.failed_data_queue.append(self.data_queue)
                self.data_queue.clear()
            time.sleep(1)


if __name__ == "__main__":
    mb = MessageBroker()
    mb.start()
