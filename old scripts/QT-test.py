from PyQt5.QtWidgets import *
app = QApplication([])
button = QPushButton('Click')
#def on_button_clicked():
#    alert = QMessageBox()
#    alert.setText('You clicked the button!')
#    alert.exec()


status = 0

def on_button_clicked():
    global status
    if status == 0:
        status = 1
    else:
        status = 0
    print(status)


button.clicked.connect(on_button_clicked)
button.show()
app.exec()