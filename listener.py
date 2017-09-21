#imports
import socket
import logging
from function_handler import Handler


#level NOTSET will print everything, CRITICAL will print nothing
logging.basicConfig(level=logging.NOTSET)

#create socket, bind to 0.0.0.0:8000
#start listening(up to 5 concurrent connections)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", 8000))
s.listen(5)

my_handler = Handler()
logging.info("[MAIN]\nBinding on all interfaces on port 8000\nObject initialized\nWaiting for connection...\n")

#Loop keeps Listener alive
while True:

    #create object with incoming connection
    my_handler.read_data(s.accept())

    #calls the function from the devices dict
    my_handler.make_request()

    logging.info("[MAIN]\nWaiting for new connection...\n")
