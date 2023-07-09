import zmq
import time
from collections import deque
import config
from threading import Thread
from threading import Lock



class Client:

    def __init__(self):
        # Create ZeroMQ context & socket of type REQ
        self.context = zmq.Context()
        self.server_socket = self.context.socket(zmq.REQ)

        # Connect server_socket to server
        self.server_socket.connect("tcp://localhost:5555")

        # Create a queue to store data for later transmission
        self.data_queue = deque()
        self.failed_data_queue = []
        self.final_processing_queue = deque()

        # connect sensor_socket to configured sensor ports
        self.sensor_socket = self.context.socket(zmq.SUB)
        self.sensor_socket.subscribe(b"")
        self.init_sensors()

        # Lock for message synchronisation
        self.data_queue_lock = Lock()
        self.final_processing_queue_lock = Lock()

    def init_sensors(self):
        """
        Initialise the sensors by connecting a socket of the client to the configured ports of the sensors
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
        Start the client processes for receiving and sending data asynchronously
        """
        try:
            rec_thread = Thread(target=self.receive_data_from_sens)
            send_thread = Thread(target=self.send_data_to_server)
            proc_thread = Thread(target=self.process_server_response)

            send_thread.start()
            rec_thread.start()
            proc_thread.start()

        except KeyboardInterrupt:
            # Cleanly exit the program on Ctrl+C
            self.server_socket.close()
            self.sensor_socket.close()
            self.context.term()

    def receive_data_from_sens(self):
        """
        Receive data from sensors and store it in a queue
        """
        while True:
            try:
                current_message = self.sensor_socket.recv_string()
                print(current_message.capitalize())
                with self.data_queue_lock:
                    self.data_queue.append(current_message)
            except zmq.ZMQError as e:
                print("Error occurred:", e)
            time.sleep(1)

    def process_server_response(self, server_response=None):
        """
        Process the server's response
        Args:
            server_response:

        Returns:

        """
        if server_response:
            print("Received response from server:", server_response)
            # TODO: Process Server Response
            # Replace this with your processing logic for the server's response

            print("Processed server response:", server_response)
        else:
            print("No response from server")
            self.failed_data_queue.extend(self.data_queue)
            self.data_queue.clear()

    def receive_data_from_server(self):
        """
        Receive data from the server and store it in a queue, needs to be called in a timed thread to make sure server
        is responding
        Returns: True if data was received

        """
        response = self.server_socket.recv_string()
        with self.final_processing_queue_lock:
            self.final_processing_queue.append(response)
        return True

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
                print("B")
                # Check if there is any failed data to send
                if self.failed_data_queue:
                    print("Sending failed data...")
                    while self.failed_data_queue:
                        # TODO: Check if data should be send one after one or in a batch
                        failed_data = self.failed_data_queue.pop()
                        self.server_socket.send_string(failed_data)
                        response = self.server_socket.recv().decode()
                        print("Received response from server:", response)
                    print("All failed data sent successfully")
                elif self.data_queue:
                    print("A")
                    with self.data_queue_lock:
                        current_message = self.data_queue.popleft()

                    print("Sending data to server:", current_message)
                    self.server_socket.send_string(current_message)

                    server_response_thread = Thread(target=self.receive_data_from_server)
                    server_response_thread.start()
                    # TODO: Define duration in config
                    duration = 5
                    server_response_thread.join(timeout=duration)

                    # Check if response was received
                    with self.final_processing_queue_lock:
                        if self.final_processing_queue:
                            server_response = self.final_processing_queue.popleft()
                            self.process_server_response(server_response)
                        else:
                            print("Function timed out.")
                            with self.data_queue_lock:
                                self.failed_data_queue.append(current_message)
                                self.failed_data_queue.extend(self.data_queue)
                                self.data_queue.clear()

            except zmq.ZMQError as e:
                print("Error occurred:", e)
                # Handle disconnection or crash here, store data in the queue
                with self.data_queue_lock:
                    self.failed_data_queue.extend(self.data_queue)
                    self.data_queue.clear()
            time.sleep(1)


if __name__ == "__main__":
    client = Client()
    client.start()
