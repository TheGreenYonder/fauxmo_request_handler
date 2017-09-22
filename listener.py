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

#create Handler object
my_handler = Handler()
logging.info("[MAIN]\nBinding on all interfaces on port 8000\nObject initialized\nWaiting for connection...\n")

loop = True
#Loop keeps Listener alive
while loop:

    #get the desired url from read_data, give it to make_request
    try:
        url = my_handler.read_data(s.accept())
        my_handler.make_request(url)
        logging.info("[MAIN]\nWaiting for new connection...\n")
    except KeyboardInterrupt:
        #when interrupting while testing, the socket will live for another few seconds - minutes, so let's catch it
        s.close()
        loop = False
        logging.info("[MAIN]\nKeyboardInterrupt - Server shutting down\n")
    except:
        logging.warning("Seems like something else went wrong\n")
