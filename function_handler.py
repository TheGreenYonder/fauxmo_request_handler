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
        self.cam1_url = "http://192.168.98.101/cgi-bin/hi3510/ptzgotopoint.cgi?&-chn=0&-point={}"
        self.tv_rcv_url = "http://192.168.98.76/send.htm?remote={}&command={}"
        self.mediola_url = "http://192.168.98.75/command?XC_FNC=SendSC&type=HM&data={}{}"


    def read_data(self, socket_accept):
        #safe and decode incoming data
        self.clientsocket, self.address = socket_accept

        tmp = self.clientsocket.recv(1024)
        self.inc_data = tmp.decode('utf-8')

        logging.info("[READ_DATA]\nConnected to: " + str(self.address[0]) + ":" + str(self.address[1]) + "\n" + self.inc_data + "\n")

        try:
            #get information from the requests header and data
            self.device = (re.search(r"device: (\w+)", self.inc_data)).group(1)
            self.identifier = (re.search(r"identifier: ([\w\d-]+)", self.inc_data)).group(1)
            self.state = (re.search(r"state=([\w\d-]+)", self.inc_data)).group(1)
            logging.info("[READ_DATA]\nDevice: " + self.device + "\nState: " + self.state + "\nIdentifier: " + self.identifier + "\n")

        except Exception:
            logging.warning("[READ_DATA]\nSomething went wrong with regex, go and fix it\n")


    def make_request(self):
        #send response to fauxmo, this way Alexa will answer with "OK"
        self.clientsocket.send(b"HTTP/1.1 200 OK\nContent-type: text/html\n\n")

        #let's wrap it in one big try catch
        try:
            #make lowercase just for some failproofing
            if self.device.lower() == "cam1":
                requests.get(self.cam1_url.format(self.state), timeout=5)

            elif self.device.lower() == "tv":
                #since the tv-remote is only used to turn the tv itself on/off and everything else is controlled through the receiver, the tv won't get its own if branch
                requests.get(self.tv_rcv_url.format(self.identifier, self.state), timeout=5)
                if self.state == "power-on":
                    requests.get(self.tv_rcv_url.format("toshiba", self.state), timeout=5)

            elif self.device.lower() == "mediola":
                requests.get(self.mediola_url.format(self.identifier, self.state), timeout=5)

            else:
                logging.debug("[CALL_FUNCTION]\nunknown device / command, check listener.py / config.json / fauxmo.py\n")

        except Exception:
            logging.warning("[CALL_FUNCTION]\nSomething went wrong while handling the request\n")

        #close client connection when all is done
        #should never fail to close but better safe than sorry, try catch
        try:
            self.clientsocket.close()
        except:
            logging.warning("[CALL_FUNCTION]\nSomething went wrong while closing the clientsocket\n")
