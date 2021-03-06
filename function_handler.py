import requests
import logging
import re


class Handler():

    def __init__(self):
        #initialize attributes for object
        self.clientsocket = None
        self.address = None
        self.inc_data = None
        self.device = None
        self.identifier = None
        self.state = None
        self.url_dict = {"cam" : ["http://192.168.98.124/cgi-bin/hi3510/ptzgotopoint.cgi?&-chn=0&-point={state}", "http://192.168.98.123/cgi-bin/hi3510/ptzgotopoint.cgi?&-chn=0&-point={state}"],
			"tv" : "http://192.168.98.76/send.htm?remote={id}&command={state}",
			"mediola" : "http://192.168.98.75/command?XC_FNC=SendSC&type=HM&data={id}{state}"}


    def read_data(self, socket_accept):
        #safe and decode incoming data, make lowercase
        self.clientsocket, self.address = socket_accept
        self.inc_data = self.clientsocket.recv(1024).decode('utf-8').lower()

        #sometimes the data received is not complete and "data" will be sent in a second message
        #obviously, if "state" is simply missing because of a config mistake
        #then this part will make listener have a hang-up
        if re.search(r"state=([\w\d-]+)", self.inc_data) is None:
            self.inc_data = self.inc_data + self.clientsocket.recv(1024).decode('utf-8').lower()

        logging.info("[READ_DATA]\nConnected to: " + str(self.address[0]) + ":" + str(self.address[1]) + "\n" + self.inc_data + "\n")

        try:
            #get information from the requests header
            self.device = re.search(r"device: (\w+)", self.inc_data).group(1)
            self.identifier = re.search(r"identifier: (\w+)", self.inc_data).group(1)
            self.state = re.search(r"state=([\w\d-]+)", self.inc_data).group(1)

            logging.info("[READ_DATA]\nDevice: " + self.device + "\nState: " + self.state + "\nIdentifier: " + self.identifier + "\n")

        except:
            logging.exception("[READ_DATA]\nSomething went wrong with regex, go and fix it\n")
            print("\n")

    def make_request(self):
        #send response to fauxmo, this way Alexa will answer with "OK"
        self.clientsocket.send(b"HTTP/1.1 200 OK\nContent-type: text/html\n\n")

        #make request to all cams
        try:
            if self.device == "cam":
                for url in self.url_dict[self.device]:
                    try:
                        requests.get(url.format(state = self.state), timeout=5)
                    except:
                        logging.info("[CALL_FUNCTION]\nIP-CAM always throws exception\n")

            else:
                requests.get(self.url_dict[self.device].format(id = self.identifier, state = self.state), timeout=5)

            #if receiver is powering on, TV itself should power on too
            if (self.device == "tv") and (self.state == "power-on"):
                requests.get(self.url_dict[self.device].format(id = "toshiba", state = self.state), timeout=5)

        except:
            #sadly, digitus cam does never answer to requests even if they accept it, therefore requests to the cam will always throw an exception
            logging.warning("[CALL_FUNCTION]\nSomething went wrong while handling the request\n")

        #close client connection when all is done
        #should never fail to close but better safe than sorry, try catch
        try:
            self.clientsocket.close()
        except:
            logging.exception("[CALL_FUNCTION]\nSomething went wrong while closing the clientsocket\n")
            print("\n")
