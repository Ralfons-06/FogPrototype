#client = local component/edge device

import zmq
import time
import random
import decimal

# Local component (Edge Device)
context = zmq.Context() #A zmq Context creates sockets via its ctx.socket method.
socket = context.socket(zmq.REP)
socket.connect("tcp://localhost:5555")

#Check for queued data
queued_data = []
try:
    with open("queued_data.txt", "r") as file:
        queued_data = file.readlines()
except FileNotFoundError:
    pass

#Send queued data to cloud
while True:

    # Generate new data 
    random_values_virtual_sensor1 = random.randint(-20, 40)
    random_values_virtual_sensor2 = random.randint(0, 500)
    random_values_virtual_sensor3 = round(decimal.Decimal(random.randrange(100, 900))/100, 1)
    
    new_data = {
        'temperature': random_values_virtual_sensor1,
        'air quality': random_values_virtual_sensor2,
        'magnitude': random_values_virtual_sensor3
    }

    # Convert data to string for transmission
    reply = str(new_data)

    # Send data to cloud component
    socket.send_string(new_data)
    print("Sent data:", new_data)
    reply = socket.recv_string()
    print("Received reply:", reply)

    # Store data in case of connection loss
    with open("queued_data.txt", "a") as file:
        file.write(new_data + "\n")

    time.sleep(1)





