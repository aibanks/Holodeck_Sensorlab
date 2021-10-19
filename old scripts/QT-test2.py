from PyQt5.QtWidgets import *
app = QApplication([])
start_button = QPushButton('Start')
stop_button = QPushButton('Stop')
#def on_button_clicked():
#    alert = QMessageBox()
#    alert.setText('You clicked the button!')
#    alert.exec()
status = 0

def on_start_button_clicked():
    global status
    if status == 0:
        print("Starting...")
        status = 1
    else:
        print("Already started. Press 'Stop' to end.")
    
def on_stop_button_clicked():
    global status
    if status == 0:
        print("Already stopped. Press 'Start' to begin.")
    else:
        print("Stopping...") 
        status = 0   

start_button.clicked.connect(on_start_button_clicked)
stop_button.clicked.connect(on_stop_button_clicked)
start_button.show()
stop_button.show()
app.exec()