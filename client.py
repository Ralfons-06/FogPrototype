import zmq
from collections import deque
import time


# Set up ZeroMQ context and socket
context = zmq.Context()
socket = context.socket(zmq.REQ)

# Connect to the server
socket.connect("tcp://localhost:5555")
print("listening")
# Create a queue to store data for later transmission
data_queue = deque()
failed_data_queue = deque()
i = 0

# Function to send sensor data to the server
def send_sensor_data(data):
    socket.send(data.encode())
    response = socket.recv().decode()
    print("Received response from server:", response)

# Function to process the server's processed sensor data
def process_server_response(response):
    # Replace this with your processing logic for the server's response
    print("Processed server response:", response)

# Fake sensor data generator
def generate_sensor_data():
    # Replace this with your actual sensor data generation logic
    return str(i) + "Sensor Data"

while True:
    try:
        # Generate sensor data
        data = generate_sensor_data()
        print(data)

        # Send sensor data to the server
        send_sensor_data(data)

        # Check if there is any failed data to send
        if failed_data_queue:
            while failed_data_queue:
                failed_data = failed_data_queue.popleft()
                send_sensor_data(failed_data)

        time.sleep(2)

    except zmq.ZMQError as e:
        print("Error occurred:", e)
        # Handle disconnection or crash here, store data in the queue
        data_queue.append(data)

    except KeyboardInterrupt:
        # Cleanly exit the program on Ctrl+C
        socket.close()
        context.term()
        break

    else:
        # Check if there is any queued data to send
        if data_queue:
            while data_queue:
                queued_data = data_queue.popleft()
                try:
                    send_sensor_data(queued_data)
                except zmq.ZMQError:
                    print("Failed to send queued data:", queued_data)
                    failed_data_queue.append(queued_data)

                # Receive and process the server's response
                response = socket.recv().decode()
                process_server_response(response)
