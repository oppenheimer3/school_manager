import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5 import QtCore
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        _translate = QtCore.QCoreApplication.translate
        layout = QVBoxLayout()
        button = QPushButton("Hover over me!")
        button.setToolTip(_translate("MainWindow", "<html><head/><body><p>open class</p><p><br/></p></body></html>"))  # Set the tooltip text here
        layout.addWidget(button)

        self.setLayout(layout)
        self.setWindowTitle("Tooltip Example")
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWidget()
    sys.exit(app.exec_())
