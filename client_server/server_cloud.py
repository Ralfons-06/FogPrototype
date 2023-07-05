#request-reply pattern
#server = cloud
#client = edge device = local component

import zmq

import random
import decimal

# Server (Cloud component)
context = zmq.Context() #A zmq Context creates sockets via its ctx.socket method.
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:

    #receive request/ data from edge device
    request = socket.recv_string() #Receive a unicode string, as sent by send_string.
    print("Received request: ", request)

    # Send reply back to edge device
    reply = "Reply from the cloud component"
    socket.send_string(reply)
    print("Sent reply: ", reply)









