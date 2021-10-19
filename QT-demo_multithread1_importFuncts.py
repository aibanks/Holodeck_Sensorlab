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
from azure.eventhub import EventHubProducerClient, EventData
import os
import time
from random import randint

#import E4_functions as Empatica_E4


class ReadingThread(QtCore.QObject):

    output = QtCore.pyqtSignal(object)
    
    def __init__(self):
        #QtCore.QObject.__init__(self)
        super(ReadingThread, self).__init__() # this way is more common to me
        
        #self.directory = directory
        self.refreshtime = 100

        self.startTime = time.time()
        # setting up a timer to substitute the need of a while loop for a 
        # repetitive task
        self.poller = QTimer(self)
        # this is the function the timer calls upon on every timeout
        self.poller.timeout.connect(self._polling_routine)

    def _polling_routine(self):
        # this is what's inside of your while loop i.e. your repetitive task
        #outstring = "test"
        #self.output.emit(outstring)
        self.device.stream(self.metadata['ParticipantName'], 
            self.metadata['ParticipantID'], self.metadata['ParticipantID'] +"_" + str(startTime))

    def polling_start(self):
        # slot to call upon when timer should start the routine.
        self.device.subscribe_to_data()
        self.output.emit([1,1])
        
        self.poller.start(self.refreshtime)
        # the argument specifies the milliseconds the timer waits in between
        # calls of the polling routine. If you want to emulate the polling
        # routine in a while loop, you could pass 0 ms...

    def polling_stop(self):
        # This simply stops the timer. The timer is still "alive" after.
        self.poller.stop()
        # create an unsubscribe() function and use it here
        self.device.unsubscribe_to_data()
        self.output.emit([1,0])

    def device_connect(self):
        #deviceID = 'CDCB11'
        con_response = self.device.connect(self.metadata['DeviceID'])
        if "R device_connect OK" in con_response:
            print('Connection Response matched for successful connection...')
            self.output.emit([1,0])
        else:
            print('Bad connection response on connection attempt')

    def device_disconnect(self):
        self.device.disconnect()
        self.output.emit([0,0])

class Example(QWidget):
    emit_connect = QtCore.pyqtSignal()
    emit_start =  QtCore.pyqtSignal()
    emit_stop = QtCore.pyqtSignal()
    emit_disconnect = QtCore.pyqtSignal()
    emit_device = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.initUI()
        self.takeinputs()
        print(self.metadata)
        print('Model #:', self.metadata['DeviceID'])
        
        self.device_dict = {"Empatica E4": "E4_functions", 'Shimmer': 'Shimmer_functions'}
        self.importdevice = self.device_dict[self.metadata['Sensor']]
        print('Importing py script', self.importdevice)
        self.init_worker()

    def takeinputs(self):
        Participant_name, done1 = QInputDialog.getText(
             self, 'Input Dialog', "<html style='font-size:12pt;'>Enter Participant's name:<br></html>")

        Participant_ID, done2 = QInputDialog.getText(
           self, 'Input Dialog', "<html style='font-size:12pt;'>Enter Participant's ID #:<br></html>")  
        
        Researcher_name, done3 = QInputDialog.getText(
              self, 'Input Dialog', "<html style='font-size:12pt;'>Enter Researcher's name:<br></html>")
  
        sensors =['Empatica E4', 'Shimmer']
        selected_sensor, done4 = QInputDialog.getItem(
          self, 'Input Dialog', "<html style='font-size:12pt;'>Select the sensor you're using:<br></html>", sensors)

        deviceID, done5 = QInputDialog.getText(
            self, 'Input Dialog', "<html style='font-size:12pt;'>Enter Device ID:<br></html>")

        if done1 and done2 and done3 and done4 and done5 :
             # Showing confirmation message along
             # with information provided by user. 
             self.label_metadata.setText('Session Information\nParticipant Name: '
                                 +str(Participant_name)+'('+str(Participant_ID)+')'+'\n'+'Researcher Name: '
                                 +str(Researcher_name)+'\nSelected Sensor: '+str(selected_sensor)
                                 +"\nDevice ID: "+str(deviceID))
             print(Participant_name)
             self.metadata = {'ParticipantName': Participant_name, 'ParticipantID': Participant_ID,
             'ResearcherName': Researcher_name, 'Sensor': selected_sensor, 'DeviceID': deviceID}
             print(self.metadata)


    def init_worker(self):
        self.thread = QtCore.QThread()
        self.worker = ReadingThread()
        self.worker.device = __import__(self.importdevice)
        self.worker.metadata = self.metadata
        
        self.worker.moveToThread(self.thread)

        ## Communicate a value across threads
        #self.worker.output.connect(self.print_new_value) 

        self.worker.output.connect(self.status_update)

        self.emit_start.connect(self.worker.polling_start)
        self.emit_stop.connect(self.worker.polling_stop)
        self.emit_connect.connect(self.worker.device_connect)
        self.emit_disconnect.connect(self.worker.device_disconnect)

        self.thread.start()

    def button_pressed_start(self):
        if self.status == [1,0]:
            self.emit_start.emit()
            self.text = resize_max_lines(self.text)
            self.text += "\nData collection started successfully. Data Collection in progress."
            self.label_status.setText(self.text)
        elif self.status == [1,1]:
            self.text = resize_max_lines(self.text)
            self.text += "\nStart button pressed but data collection is already in progress. Press the stop button to stop data collection."
            self.label_status.setText(self.text)
        else:
            print('Status must be [1,0], but its at: ', self.status)
            self.text = resize_max_lines(self.text)
            self.text += "\nMust connect device before data collection can start."
            self.label_status.setText(self.text)

    def button_pressed_stop(self):
        if self.status == [1,1]:
            self.emit_stop.emit()
            self.text = resize_max_lines(self.text)
            self.text += "\nStopped data collection."
            self.label_status.setText(self.text)
        else:
            print('Status must be [1,1], but its at: ', self.status)
            self.text = resize_max_lines(self.text)
            self.text += "\nStop button pressed but data collection is not in progress."
            self.label_status.setText(self.text)

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
            #self.text = "Press 'Connect' to establish connection with the device."
            #self.label_status.setText(self.text)
            self.text = resize_max_lines(self.text)
            self.text += "\nConnected to device. Press 'Start' to begin data collection or 'Disconnect' to disconnect device."
            self.label_status.setText(self.text)
        else:
            print('Connection Button Pressed but Already Connected')
            self.text = resize_max_lines(self.text)
            self.text += "\nConnection Button pressed but device is already connected."
            self.label_status.setText(self.text)

    def button_pressed_disconnect(self):
        if self.status == [1,0]:
            print('Disconnect button pressed while status == ', self.status)
            self.emit_disconnect.emit()
            self.text = resize_max_lines(self.text)
            self.text += "\nSuccessfully disconnected from device."
            self.label_status.setText(self.text)
        else:
            print('Status must be at [1,0] to disconnect, but status is:', self.status)
            self.text = resize_max_lines(self.text)
            self.text += "\nDevice not connected.  Disconnection attempt unsuccessful."
            self.label_status.setText(self.text)

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
        startb.clicked.connect(self.button_pressed_start)
        #startb.setEnabled(False)

        stopb = QPushButton('Stop Data Collection', self)
        stopb.setFont(QFont('Arial', 20))
        stopb.clicked.connect(self.button_pressed_stop)
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
        self.text = "Press 'Connect' to establish connection with the device."
        self.label_status.setText(self.text)
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
        #vbox.addLayout(datastreams_chkbx)

        #self.setFixedWidth(1500)
        #self.setFixedHeight(500)
        self.showMaximized()
        #self.move(1000, 500)
        self.setWindowTitle('Data Streaming Menu')
        self.show()

participant = "Tony Banks"    # need to generalize
participant_ID = "001"
startTime = time.time()
session_ID = participant_ID +"_" + str(startTime)

def resize_max_lines(text_str):
    '''
    Resize the input text string so it has a maximum of 6 new lines, eliminating the first lines and keeping the end lines.  
    :input text_str: string
    :return resized_text_str: string
    '''
    line_split_list = text_str.split('\n')
    if len(line_split_list) >= 6:
        i = len(line_split_list) - 5
        resized_text_str = '\n'.join(line_split_list[i:])
    else:
        resized_text_str = text_str
    return resized_text_str

def main():

    app = QApplication(sys.argv)
    ex = Example()
      
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()