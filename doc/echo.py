import socket
import sys
import string
import random
import time
import threading
from threading import Lock
import logging
import logging.handlers
from logging.handlers import RotatingFileHandler
def setupLogger():
    logger = logging.getLogger("")
    handler = RotatingFileHandler("./logs/proxy.log", maxBytes=5242880, backupCount=14)
    formatter = logging.Formatter('%(asctime)s: %(message)s', '%b %d %H:%M:%S')
    formatter.converter = time.gmtime  # if you want UTC time
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

connections = []
loggingLock = Lock()
loggingLines = []


def addLog(msg):
    global loggingLock
    global loggingLines
    with loggingLock:
        loggingLines.append(msg)

def logWorker():
    global loggingLock
    global loggingLines
    setupLogger()
    while True:
        with loggingLock:
            for line in loggingLines:
                logging.info(line)
            loggingLines = []
        time.sleep(1)

class Client(threading.Thread):
    def __init__(self, socket, address, name, signal):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.name = name
        self.signal = signal

    def run(self):
        count = 0
        while True:
            count += 1
            if count >= 100000:
                break
            try:
                data = self.socket.recv(10240)
                addLog("Echo to " + str(self.address) + " %d bytes" %(len(data)))
                self.socket.sendall(data)
            except:
                break
        addLog("Refreshing " + str(self.address) + "")
        self.socket.close()
        connections.remove(self)

log_thread = threading.Thread(target=logWorker, args=())
log_thread.start()

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
# Bind the socket to the port
server_address = ("193.135.9.63", 31845)
sock.bind(server_address)
# Listen for incoming connections
sock.listen(128)

while True:
    sockClient, address = sock.accept()
    connections.append(Client(sockClient, address, "Name", True))
    connections[len(connections) - 1].start()