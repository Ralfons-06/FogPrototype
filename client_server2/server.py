import zmq
import random
from collections import deque

# Create ZeroMQ context & socket of type REP 
context = zmq.Context()
socket = context.socket(zmq.REP)

# Bind socket to a specific port
socket.bind("tcp://*:5555")
print("Server is listening")

# Create a queue to store data for later processing
data_queue = deque()
failed_data_queue = deque()

# Generate data
def humidity_sensor():
    humidity = random.uniform(0, 100)
    return humidity

while True:
    try:
        # Wait for a request from the client
        request = socket.recv_string()
        print("Received request: {}".format(request))

        # Send the processed data back to the client
        response = "Message received: {}. Current humidity level: {:.2f}".format(request, humidity_sensor())
        socket.send_string(response)

    except zmq.ZMQError as e:
        print("Error occurred:", e)
        # Handle disconnection or crash here, queue the data for later processing
        data_queue.append(humidity_sensor())

    except KeyboardInterrupt:
        # Cleanly exit the program on Ctrl+C
        socket.close()
        context.term()
        break