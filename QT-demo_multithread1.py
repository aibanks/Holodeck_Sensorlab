from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer

import sys
import socket
import time
from datetime import datetime 
import requests
import json
#from azure.eventhub import EventHubProducerClient, EventData
import os
import time
from random import randint


class ReadingThread(QtCore.QObject):

    output = QtCore.pyqtSignal(object)
    
    def __init__(self):
        #QtCore.QObject.__init__(self)
        super(ReadingThread, self).__init__() # this way is more common to me
        
        #self.directory = directory
        self.refreshtime = 50

        # setting up a timer to substitute the need of a while loop for a 
        # repetitive task
        self.poller = QTimer(self)
        # this is the function the timer calls upon on every timeout
        self.poller.timeout.connect(self._polling_routine)

    def _polling_routine(self):
        # this is what's inside of your while loop i.e. your repetitive task
        #outstring = "test"
        #self.output.emit(outstring)
        stream()

    def polling_start(self):
        # slot to call upon when timer should start the routine.
        subscribe_to_data()
        self.output.emit([1,1])
        self.poller.start(self.refreshtime)
        # the argument specifies the milliseconds the timer waits in between
        # calls of the polling routine. If you want to emulate the polling
        # routine in a while loop, you could pass 0 ms...

    def polling_stop(self):
        # This simply stops the timer. The timer is still "alive" after.
        self.poller.stop()
        # create an unsubscribe() function and use it here
        unsubscribe_to_data()
        self.output.emit([1,0])

    def device_connect(self):
        con_response = connect()
        if "R device_connect OK" in con_response:
            print('Connection Response matched for successful connection...')
            self.output.emit([1,0])
        else:
            print('Bad connection response on connection attempt')

    def device_disconnect(self):
        disconnect()
        self.output.emit([0,0])

class Example(QWidget):
    emit_connect = QtCore.pyqtSignal()
    emit_start =  QtCore.pyqtSignal()
    emit_stop = QtCore.pyqtSignal()
    emit_disconnect = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.initUI()
        self.init_worker()
        self.takeinputs()

    def takeinputs(self):
        Participant_name, done1 = QInputDialog.getText(
             self, 'Input Dialog', "<html style='font-size:12pt;'>Enter Participant's name:<br></html>")

        Participant_ID, done2 = QInputDialog.getInt(
           self, 'Input Dialog', "<html style='font-size:12pt;'>Enter Participant's ID #:<br></html>")  
        
        Researcher_name, done3 = QInputDialog.getText(
              self, 'Input Dialog', "<html style='font-size:12pt;'>Enter Researcher's name:<br></html>")
  
        sensors =['Empatica E4', 'Shimmer']
        selected_sensor, done4 = QInputDialog.getItem(
          self, 'Input Dialog', "<html style='font-size:12pt;'>Select the sensor you're using:<br></html>", sensors)
  
        if done1 and done2 and done3 and done4 :
             # Showing confirmation message along
             # with information provided by user. 
             self.label_metadata.setText('Session Information\nParticipant Name: '
                                 +str(Participant_name)+'('+str(Participant_ID)+')'+'\n'+'Researcher Name: '
                                 +str(Researcher_name)+'\nSelected Sensor: '+str(selected_sensor))
             print(Participant_name)
             self.metadata = [Participant_name, Participant_ID, Researcher_name, selected_sensor]
             print(self.metadata)

    def init_worker(self):
        self.thread = QtCore.QThread()
        
        self.worker = ReadingThread()
        self.worker.moveToThread(self.thread)

        ## Communicate a value across threads
        #self.worker.output.connect(self.print_new_value) 

        self.worker.output.connect(self.status_update)

        self.emit_start.connect(self.worker.polling_start)
        self.emit_stop.connect(self.worker.polling_stop)
        self.emit_connect.connect(self.worker.device_connect)
        self.emit_disconnect.connect(self.worker.device_disconnect)

        self.thread.start()

    def start_polling(self):
        if self.status == [1,0]:
            self.emit_start.emit()
        else:
            print('Status must be [1,0], but its at: ', self.status)

    def stop_polling(self):
        if self.status == [1,1]:
            self.emit_stop.emit()
        else:
            print('Status must be [1,1], but its at: ', self.status)

    def finish_worker(self):
        # for sake of completeness: call upon this method if you want the
        # thread gone. E.g. before closing your application.
        # You could emit a finished sig from your worker, that will run this.
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

    #def print_new_value(self, value):
    #    print(value)

    def status_update(self, status):
        self.status = status
        print("Status updated to ", self.status)

    def button_pressed_connect(self):
        if self.status == [0,0]:
            print('connect button pressed while status == [0,0]')
            self.emit_connect.emit()
        else:
            print('Connection Button Pressed but Already Connected')

    def button_pressed_disconnect(self):
        if self.status == [1,0]:
            print('Disconnect button pressed while status == ', self.status)
            self.emit_disconnect.emit()
        else:
            print('Status must be at [1,0] to disconnect, but status is:', self.status)

    def initUI(self):

        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        vbox = QVBoxLayout()
        

        self.col = QColor(0, 0, 0)

        deviceconnectb = QPushButton('Connect to Device', self)
        deviceconnectb.setFont(QFont('Arial', 20))
        deviceconnectb.clicked.connect(self.button_pressed_connect)  #self.printMessage)

        startb = QPushButton('Start Data Collection', self)
        startb.setFont(QFont('Arial', 20))
        startb.clicked.connect(self.start_polling)
        #startb.setEnabled(False)

        stopb = QPushButton('Stop Data Collection', self)
        stopb.setFont(QFont('Arial', 20))
        stopb.clicked.connect(self.stop_polling)
        #stopb.setEnabled(False)

        devicedisconnectb = QPushButton('Disconnect from Device', self)
        devicedisconnectb.setFont(QFont('Arial', 20))
        devicedisconnectb.clicked.connect(self.button_pressed_disconnect)
        #devicedisconnectb.setEnabled(False)

        hbox1.addWidget(deviceconnectb)
        hbox1.addWidget(startb)
        hbox1.addWidget(stopb)
        hbox1.addWidget(devicedisconnectb)

        #vbox.addLayout(hbox)
        #vbox.addWidget(self.square)

        self.setLayout(vbox)

        #self.text = 'First establish connection to device'
        #global status
        self.status = [0, 0] #initial status, not connected, not started

        self.label_status = QLabel(self)
        self.label_status.setText("Ensure the device is connected to the E4 Streaming Server,\nthen press 'Connect' to establish connection with the device.")
        self.label_status.setFont(QFont('Arial', 14))
        #grid = QGridLayout()
        #hbox2.addWidget(self.label_status) #Qt.AlignTop)


        self.label_metadata = QLabel(self)
        self.label_metadata.setText("")
        self.label_metadata.setFont(QFont('Arial', 14))
        #self.label_metadata.setAlignment(QtCore.Qt.AlignRight)
        hbox2.addWidget(self.label_metadata)
        hbox2.addWidget(self.label_status)

        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        #self.setFixedWidth(1500)
        #self.setFixedHeight(500)
        self.showMaximized()
        #self.move(1000, 500)
        self.setWindowTitle('Data Streaming Menu')
        self.show()


#participant = input("Participant's Full Name: ")
#participant_ID = input("Participant ID: ")
participant = "Tony Banks"
participant_ID = "001"
startTime = time.time()
session_ID = participant_ID +"_" + str(startTime)

# SELECT DATA TO STREAM
acc = True      # 3-axis acceleration
bvp = True     # Blood Volume Pulse
gsr = True      # Galvanic Skin Response (Electrodermal Activity)
tmp = True      # Temperature
ibi = True      # Interbeat Interval and Heartbeat
bat = True      # Device Battery
tag = True     # Tag taken from the device (by pressing the button)

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
    connection_response = s.recv(bufferSize)
    connection_response = connection_response.decode("utf-8")
    print(connection_response)

    print("Pausing data receiving")
    s.send("pause ON\r\n".encode())
    response = s.recv(bufferSize)
    print(response.decode("utf-8"))

    return connection_response
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

def stream():
    response = s.recv(bufferSize).decode("utf-8")
    print(response)
    #print('Data streaming in progress')
    if "connection lost to device" in response:
        print(response.decode("utf-8"))
        reconnect()
    #samples = response.split("\r\n")
    #print(samples)

def unsubscribe_to_data():
    global acc, bvp, gsr, tmp, ibi, bat, tag
    if acc:
        print("Unsubscribing to ACC")
        s.send(("device_subscribe " + 'acc' + " OFF\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if bvp:
        print("Unsubscribing to BVP")
        s.send(("device_subscribe " + 'bvp' + " OFF\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if gsr:
        print("Unsubscribing to GSR")
        s.send(("device_subscribe " + 'gsr' + " OFF\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if tmp:
        print("Unsubscribing to Temp")
        s.send(("device_subscribe " + 'tmp' + " OFF\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if ibi:
        print("Unsubscribing to IBI")
        s.send(("device_subscribe " + 'ibi' + " OFF\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if bat:
        print("Unsubscribing to Batt")
        s.send(("device_subscribe " + 'bat' + " OFF\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))
    if tag:
        print("Unsubscribing to Tag")
        s.send(("device_subscribe " + 'tag' + " OFF\r\n").encode())
        response = s.recv(bufferSize)
        print(response.decode("utf-8"))


def main():

    app = QApplication(sys.argv)
    ex = Example()
      
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()