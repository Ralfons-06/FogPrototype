import zmq
import random
import time 
from collections import deque
#from virtual_sensor import VirtualSensor


# Create ZeroMQ context & socket of type REQ
context = zmq.Context()
socket = context.socket(zmq.REQ)

# Connect socket to server
socket.connect("tcp://localhost:5555")

# Create a queue to store data for later transmission
data_queue = deque()
failed_data_queue = deque()
i = 0

# Fake sensor data generator
def temperature_sensor():
    temperature = random.uniform(-20, 40)
    return temperature

def air_quality_sensor():
    air_quality = random.uniform(0, 500)
    return air_quality
    

while True:
    try:
        # Check if there is any queued data to send
        if data_queue:
            queued_data = data_queue.popleft()

            try:
                socket.send_string(queued_data)
            except zmq.ZMQError:
                    print("Failed to send queued data:", queued_data)
                    failed_data_queue.append(queued_data)
        
        else:    
            # Generate random data
            message = "Current temperature: {:.1f}°C and Air Quality: {:.0f}".format(temperature_sensor(), air_quality_sensor())
            print(message)

            # Send sensor data to the server
            socket.send_string(message)

        # Receive the server's response
        response = socket.recv_string()
        print("Server response: {}".format(response))

        # Check if the user wants to quit
        if message.lower() == "quit":
            print("Quitting...")
            break

        time.sleep(2)

    except zmq.ZMQError as e:
        print("Error occurred:", e)
        # Handle disconnection or crash here, store data in the queue
        data_queue.append(temperature_sensor(),air_quality_sensor())

    except ValueError as e:
        print("Input Error occurred: {}".format(str(e)))
        # Handle the error as needed

    except KeyboardInterrupt:
        # Cleanly exit the program on Ctrl+C
        socket.close()
        context.term()
        break