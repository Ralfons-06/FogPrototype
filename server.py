import zmq
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


# Function to process received sensor data
def process_sensor_data(received_data):
    # Replace this with your actual sensor data processing logic
    topic = received_data.split(" ")[0]
    value = int(received_data.split(" ")[1])
    match topic.lower():
        case "temperature":
            if value < 0:
                return "Too cold"
            elif value > 30:
                return "Too hot"
            else:
                return "Temperature OK"
        case "air_quality":
            if value > 50:
                return "Bad air quality"
            else:
                return "Air quality OK"
        case "humidity":
            if value > 80:
                return "Too humid"
            elif value < 30:
                return "Too dry"
            else:
                return "Humidity OK"
        case _:
            return "Unknown topic"


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
