import zmq
import random
import time
from collections import deque
from virtual_sensor import VirtualSensor
import config
from multiprocessing import Process


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
        self.sensor_ports = self.find_active_sensor_ports()
        self.sensor_socket = self.context.socket(zmq.SUB)

    def find_active_sensor_ports(self):
        print("START: Looking for active sensors...")
        sensor_ports = {}
        current_conf = config.VirtualSensorConfig.SENSORS
        for sensor in current_conf.keys():
            sensor_ports[sensor] = current_conf.get(sensor).get("Port")
            print(f"Found sensor {sensor.upper()} with port {current_conf.get(sensor).get('Port')}")
        print("END: Looking for active sensors...")
        return sensor_ports

    def start(self):
        # Connect client and sensors
        # sensor_socket = self.context.socket(zmq.SUB)

        for sensor in self.sensor_ports.items():
            self.sensor_socket.connect(f"tcp://localhost:%s" % sensor[1])
            print(f"Successfully connected to sensor {sensor[0]} on port {sensor[1]}")
        self.sensor_socket.subscribe(b"")

        current_message = "Initialize"

        # TODO: multithread receiving and sending so that message broker can receive and send at the same time
        while True:
            # Listen to sensor ports for incoming data
            # Send data to the server
            # TODO: multihreading
            try:
                # Check if there is any queued data to send
                if self.data_queue:
                    queued_data = self.data_queue.popleft()

                    try:
                        self.server_socket.send_string(queued_data)
                    except zmq.ZMQError:
                        print("Failed to send queued data:", queued_data)
                        self.failed_data_queue.append(queued_data)

                else:
                    # Generate data
                    # message = "Current temperature: {:.1f}°C and Air Quality: {:.0f}".format(temperature_sensor(), air_quality_sensor())

                    current_message = sensor_socket.recv_string()
                    print(current_message)

                    # Send sensor data to the server
                    self.server_socket.send_string(current_message)

                # Receive the server's response
                response = self.server_socket.recv_string()
                print("Server response: {}".format(response))

                # Check if the user wants to quit
                if current_message.lower() == "quit":
                    print("Quitting...")
                    break

                time.sleep(2)

            except zmq.ZMQError as e:
                print("Error occurred:", e)
                # Handle disconnection or crash here, store data in the queue
                # self.data_queue.append(temperature_sensor(), air_quality_sensor())
                self.data_queue.append(current_message)

            except ValueError as e:
                print("Input Error occurred: {}".format(str(e)))
                # Handle the error as needed

            except KeyboardInterrupt:
                # Cleanly exit the program on Ctrl+C
                self.server_socket.close()
                sensor_socket.close()
                self.context.term()
                break

    def receive_data_from_sens(self):
        while True:
            current_message = sensor_socket.recv_string()
            print(current_message)
            self.data_queue.append(current_message)


    def send_data_to_cloud_comp(self):
        while True:
            if self.data_queue:
                self.server_socket.send_string(self.data_queue.popleft())



if __name__ == "__main__":
    mb = MessageBroker()
    mb.start()
