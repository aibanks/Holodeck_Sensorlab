from To_Azure_Eventhub import disconnect
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import socket
import time
from datetime import datetime 
import requests
import json
from azure.eventhub import EventHubProducerClient, EventData
import os
import time
from random import randint

class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        hbox = QHBoxLayout()
        vbox = QVBoxLayout()

        self.col = QColor(0, 0, 0)

        deviceconnectb = QPushButton('Connect to Device', self)
        deviceconnectb.setFont(QFont('Arial', 20))
        deviceconnectb.clicked.connect(self.printMessage)

        startb = QPushButton('Start Data Collection', self)
        startb.setFont(QFont('Arial', 20))
        startb.clicked.connect(self.printMessage)

        stopb = QPushButton('Stop Data Collection', self)
        stopb.setFont(QFont('Arial', 20))
        stopb.clicked.connect(self.printMessage)

        devicedisconnectb = QPushButton('Disconnect from Device', self)
        devicedisconnectb.setFont(QFont('Arial', 20))
        devicedisconnectb.clicked.connect(self.printMessage)

        hbox.addWidget(deviceconnectb)
        hbox.addWidget(startb)
        hbox.addWidget(stopb)
        hbox.addWidget(devicedisconnectb)

        """ self.square = QFrame(self)
        self.square.setFixedSize(180, 180)
        self.square.setStyleSheet("QWidget { background-color: %s }" %
                                  self.col.name()) """

        vbox.addLayout(hbox)
        #vbox.addWidget(self.square)

        self.setLayout(vbox)

        self.text = 'First establish connection to device'
        global status
        status = [0, 0] #initial status, not connected, not started

        self.label = QLabel(self.text, self)
        self.label.setFont(QFont('Arial', 14))
        #grid = QGridLayout()
        vbox.addWidget(self.label) #Qt.AlignTop)

        #self.setFixedWidth(1500)
        #self.setFixedHeight(500)
        self.showMaximized()
        #self.move(1000, 500)
        self.setWindowTitle('Data Streaming Menu')
        self.show()

    def printSelf(self):
        source = self.sender()
        print(source.text())

    def printMessage(self):
        source = self.sender()
        print(f'Pressed: {source.text()}')
        global status
        if source.text() == 'Connect to Device':
            if status[0] == 0: #Device not connected
                #Add functionality to trigger function to connect the device
                #Function should add method to trigger new status once connected
                self.text = "Connecting to device...\n...\n...\nConnected to device. Press 'Start Data Collection' to begin data collection."
                connect()
                time.sleep(1)
                subscribe_to_data()
                status[0] = 1
            elif status == [1, 0]: #Device already connected and data collection not started
                self.text = "Already connected to device. Press 'Start Data Collection' to begin data collection."
            else: #Device already connected and data collection already started. Status == [1, 1]
                self.text = "Already connected to device and data collection is in progress.\nPress 'Stop Data Collection' to stop data collection."
            #self.label.setText(self.text)
        elif source.text() == "Start Data Collection":
            if status[0] == 0: #Device not connected
                self.text = "Device not connected.  Connect device before starting data collection."
            elif status == [1, 0]:  #Device already connected and data collection not started
                self.text = "Starting data collection...\n...\n...\nData collection in progress.  Press 'Stop Data Collection' to terminate data collection."
                stream()
                status = [1, 1]
            else: #Device already connected and data collection already started. Status == [1, 1]
                self.text = "Already connected to device and data collection is in progress.\nPress 'Stop Data Collection' to stop data collection."
            self.label.setText(self.text)
        elif source.text() == "Stop Data Collection":
            if status[0] == 0: #Device not connected
                self.text = "Device not connected.  Connect device before starting data collection."
            elif status == [1, 0]: #Device connected and data collection not started
                self.text = "Data collection not started. Press 'Start Data Collection' to begin data collection."
            else: #Device already connected and data collection already started. Status == [1, 1]
                self.text = "Stopping data collection.\n...\n...\nData collection stopped.\nPress 'Start Data Collection' to resume data collection.\nPress 'Disconnect Device' to disconnect from device."
                status = [1, 0]
        elif source.text() == 'Disconnect from Device':
            if status[0] == 0: #Device not connected
                self.text = "Device already disconnected."
            elif status == [1, 0]: #Device connected.  Not collecting data
                self.text = "Disconnecting from device.\n...\n...\nDisconnected from device."
                disconnect()
                status = [0, 0]
            else: #Device connected and data collection in progress
                self.text = "Data collection in progress.\nStop data collection before disconnecting from device."
        self.label.setText(self.text)


participant = input("Participant's Full Name: ")
participant_ID = input("Participant ID: ")
startTime = time.time()
session_ID = participant_ID +"_" + str(startTime)

# SELECT DATA TO STREAM
acc = True      # 3-axis acceleration
bvp = True     # Blood Volume Pulse
gsr = True      # Galvanic Skin Response (Electrodermal Activity)
tmp = True      # Temperature
ibi = True      # Interbeat Interval and Heartbeat
bat = False      # Device Battery
tag = False     # Tag taken from the device (by pressing the button)

serverAddress = '127.0.0.1'
serverPort = 28000
bufferSize = 4096

deviceID = 'CDCB11' # 'A03003'

def connect():
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)

    print("Connecting to server")
    s.connect((serverAddress, serverPort))
    print("Connected to server\n")

    print("Devices available:")
    s.send("device_list\r\n".encode())
    response = s.recv(bufferSize)
    print(response.decode("utf-8"))

    print("Connecting to device")
    s.send(("device_connect " + deviceID + "\r\n").encode())
    response = s.recv(bufferSize)
    print(response.decode("utf-8"))

    print("Pausing data receiving")
    s.send("pause ON\r\n".encode())
    response = s.recv(bufferSize)
    print(response.decode("utf-8"))
#connect()

#time.sleep(1)

def subscribe_to_data():
    global acc, bvp, gsr, tmp, ibi, bat, tag
    if acc:
        print("Subscribing to ACC")
        s.send(("device_subscribe " + 'acc' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if bvp:
        print("Subscribing to BVP")
        s.send(("device_subscribe " + 'bvp' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if gsr:
        print("Subscribing to GSR")
        s.send(("device_subscribe " + 'gsr' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if tmp:
        print("Subscribing to Temp")
        s.send(("device_subscribe " + 'tmp' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if ibi:
        print("Subscribing to IBI")
        s.send(("device_subscribe " + 'ibi' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if bat:
        print("Suscribing to Batt")
        s.send(("device_subscribe " + 'bat' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if tag:
        print("Subscribing to Tag")
        s.send(("device_subscribe " + 'tag' + " ON\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))

    print("Resuming data receiving")
    s.send("pause OFF\r\n".encode())
    response = s.recv(bufferSize)
    print(response.decode("utf-8"))
#subscribe_to_data()

def disconnect():
    print("Disconnecting device")
    s.send("device_disconnect\r\n".encode())

def reconnect():
    print("Reconnecting...")
    connect()
    subscribe_to_data()

def convert_to_json(sample):
    stream_type = sample.split()[0]
    if stream_type == "E4_Acc":
        new_timestamp = datetime.fromtimestamp(float(sample.split()[1])).isoformat(sep=' ', timespec='milliseconds') #recent update to include milliseconds
        new_timestamp_unix = sample.split()[1] #recent update to include unix timestamp to make querying easier
        new_data = [int(samples[i].split()[2].replace(',','.')), int(samples[i].split()[3].replace(',','.')), int(samples[i].split()[4].replace(',','.'))]
        sample_jsonX = {"stream_type" : "E4_Acc_X", "Value" : new_data[0], "dateTime" : new_timestamp, "dateTime_Unix" : new_timestamp_unix, "Session_ID" : session_ID, "Participant" : participant, "Participant_ID" : participant_ID}
        sample_jsonY = {"stream_type" : "E4_Acc_Y", "Value" : new_data[1], "dateTime" : new_timestamp, "dateTime_Unix" : new_timestamp_unix, "Session_ID" : session_ID, "Participant" : participant, "Participant_ID" : participant_ID}
        sample_jsonZ = {"stream_type" : "E4_Acc_Z", "Value" : new_data[2], "dateTime" : new_timestamp, "dateTime_Unix" : new_timestamp_unix, "Session_ID" : session_ID, "Participant" : participant, "Participant_ID" : participant_ID}
        sample_json = [sample_jsonX, sample_jsonY, sample_jsonZ]
        sample_json = json.dumps(sample_json)    #might have issues from trying to batch more than 1 json at a time later in the code
    else:
        new_timestamp = datetime.fromtimestamp(float(sample.split()[1])).isoformat(sep=' ', timespec='milliseconds') #recent update to include milliseconds
        new_timestamp_unix = sample.split()[1] #recent update to include unix timestamp to make querying easier
        new_data = float(sample.split()[2])
        sample_json = {"stream_type" : stream_type, "Value" : new_data, "dateTime" : new_timestamp, "dateTime_Unix" : new_timestamp_unix, "Session_ID" : session_ID, "Participant" : participant, "Participant_ID" : participant_ID}
        sample_json = json.dumps(sample_json)
    return(sample_json)

def stream():
    global status
    while status == [1,1]:
        response = s.recv(bufferSize).decode("utf-8")
        #print(response)
        if "connection lost to device" in response:
            print(response.decode("utf-8"))
            reconnect()
        event_data_batch = client.create_batch()
        samples = response.split("\r\n")
        for i in range(len(samples)-1):
            sample_json = convert_to_json(samples[i])
            #print(sample_json)
            event_data_batch.add(EventData(sample_json))
        client.send_batch(event_data_batch)
        print("Data streaming in progress")





def main():

    app = QApplication(sys.argv)
    ex = Example()
      
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()