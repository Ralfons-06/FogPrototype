import zmq
from collections import deque

# Set up ZeroMQ context and socket
context = zmq.Context()
socket = context.socket(zmq.REP)

# Bind the socket to a specific port
socket.bind("tcp://*:5555")

# Create a queue to store data for later processing
data_queue = deque()
failed_data_queue = deque()

# Function to process received sensor data
def process_sensor_data(data):
    # Replace this with your actual sensor data processing logic
    return "Processed Data"

while True:
    try:
        # Wait for a request from the client
        data = socket.recv().decode()

        # Process the received sensor data
        processed_data = process_sensor_data(data)

        # Send the processed data back to the client
        socket.send(processed_data.encode())

        # Check if there is any failed data to process
        if failed_data_queue:
            while failed_data_queue:
                failed_data = failed_data_queue.popleft()
                processed_data = process_sensor_data(failed_data)
                # Send the processed data back to the client
                socket.send(processed_data.encode())

    except zmq.ZMQError as e:
        print("Error occurred:", e)
        # Handle disconnection or crash here, queue the data for later processing
        data_queue.append(data)

    except KeyboardInterrupt:
        # Cleanly exit the program on Ctrl+C
        socket.close()
        context.term()
        break

    else:
        # Check if there is any queued data to process
        if data_queue:
            while data_queue:
                queued_data = data_queue.popleft()
                try:
                    processed_data = process_sensor_data(queued_data)
                    # Send the processed data back to the client
                    socket.send(processed_data.encode())
                except zmq.ZMQError:
                    print("Failed to process queued data:", queued_data)
                    failed_data_queue.append(queued_data)