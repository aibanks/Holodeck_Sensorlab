from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys


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
                status = [0, 0]
            else: #Device connected and data collection in progress
                self.text = "Data collection in progress.\nStop data collection before disconnecting from device."
        self.label.setText(self.text)

def main():

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()