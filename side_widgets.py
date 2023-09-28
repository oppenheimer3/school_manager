from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QLabel, QDialog, QVBoxLayout, QPushButton, QLineEdit
from UI.PY.subjects_list import Ui_subjects_list
from UI.PY.classroom_list import Ui_classroom_list
from UI.PY.add_class_filter import Ui_add_filter
from UI.PY.time_management import Ui_time_management
from UI.PY.cam_widget import Ui_cam_widget
from data_base import Users
from PyQt5.QtCore import  QTimer, pyqtSignal
import cv2
from pyzbar import pyzbar
from PyQt5.QtGui import QImage, QPixmap



class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setStyleSheet("background-color: rgb(61, 56, 70);\n"
        "color: rgb(255, 255, 255);\n"
        "font-family: \"Century Gothic\";\n"
        "font-size:15px")
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.check_login)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        self.setLayout(layout)
        self.Users = Users()
        if len(self.Users.get_all()) == 0:
            self.Users.add('admin', 'admin', 'manager')
    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        self.user = self.Users.get(username)
        self.accept()
        if password == self.user["password"]:
            self.accept()  
        else:
            print("Invalid credentials!")


class SubjectList(QWidget):
    def __init__(self, subjects) -> None:
        super().__init__()
        self.subjects = subjects
        self.ui = Ui_subjects_list()
        self.ui.setupUi(self)
        self.ui.subjects_table.setModel(subjects)
        self.ui.add_button.clicked.connect(self.add_subject)
        self.ui.delete_button.clicked.connect(lambda: self.subjects.delete(self.subjects.selectedRecord(self.ui.subjects_table)['subject_name']))
    def add_subject(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("add subject")
        
        layout = QVBoxLayout()
        label = QLabel("Enter subject name:")
        layout.addWidget(label)
        
        input_widget = QLineEdit()
        layout.addWidget(input_widget)
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(lambda: (self.subjects.add(input_widget.text()), dialog.close()))
        layout.addWidget(ok_button)
        
        dialog.setLayout(layout)
        dialog.exec_()


class ClassroomList(QWidget):
    def __init__(self, classrooms) -> None:
        super().__init__()
        self.classrooms = classrooms
        self.ui = Ui_classroom_list()
        self.ui.setupUi(self)
        self.ui.classroom_table.setModel(classrooms)
        self.ui.add_button.clicked.connect(self.add_classroom)
        self.ui.delete_button.clicked.connect(lambda: self.classrooms.delete(self.classrooms.selectedRecord(self.ui.classroom_table)['classroom_name']))
    def add_classroom(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("add classroom")
        
        layout = QVBoxLayout()
        label = QLabel("Enter classroom name:")
        layout.addWidget(label)
        
        input_widget = QLineEdit()
        layout.addWidget(input_widget)
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(lambda: (self.classrooms.add(input_widget.text()), dialog.close()))
        layout.addWidget(ok_button)
        
        dialog.setLayout(layout)
        dialog.exec_()

class AddClassFilter(QWidget):
    def __init__(self, tables) -> None:
        super().__init__()
        self.tables = tables
        self.ui = Ui_add_filter()
        self.ui.setupUi(self)
        self.ui.add_button.clicked.connect(self.add_filter)
        self.ui.cancel_button.clicked.connect(lambda: self.close())
        
    def add_filter(self):
        self.tables[8].add(self.ui.comboBox.currentText(), self.ui.lineEdit.text())
        filter_query = ''
        for i, filter in enumerate(self.tables[8].get_all()):
            if i != 0:
                filter_query += ' AND '
            filter_query+= f"{filter['column']} = '{filter['value']}'" 
        self.tables[2].setFilter(filter_query)
        self.close()
    
    def show(self):
        super().show()
        self.ui.comboBox.clear()
        for key in self.tables[2].fields.keys():
            if key in [i['column'] for i in self.tables[8].get_all()]:
                continue
            else: self.ui.comboBox.addItem(key)
                
        


class ClickableLabel(QLabel):
    clicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.animation = QtCore.QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QtCore.QEasingCurve.OutBack)
        self.setStyleSheet(
                    """
                            QLabel {
                                color: white;
                                background-color: #333333;
                                padding: 5px;
                                border: 1px solid #555555;
                                border-radius: 10px;  /* Add rounded edges */
                                font-size:20px
                            }

                            QLabel:hover {
                                background-color: #444444;
                            }
                        """
        )

    def enterEvent(self, event):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(-5, -5, 5, 5))
        self.animation.start()

    def leaveEvent(self, event):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry().adjusted(5, 5, -5, -5))
        self.animation.start()

    def mousePressEvent(self, event):
        self.clicked.emit()


from delegate import MultiLineDelegate
class TimeManagementWidget(QWidget):
    def __init__(self, tables) -> None:
        super().__init__()
        self.ui = Ui_time_management()
        self.ui.setupUi(self)
        self.tables = tables
        self.delegate = MultiLineDelegate()
        self.ui.tableView.setModel(self.tables[9])
        self.ui.tableView.setItemDelegate(self.delegate)

    def show(self):
        self.tables[9].delete_all()
        super().show()
        time = sorted(list(set([t['start_time'] for t in self.tables[2].get_all()] + [t['end_time'] for t in self.tables[2].get_all()])))
        for item in time:
            self.tables[9].add(item,'-','-','-','-','-','-','-') 
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            self.tables[2].setFilter(f"day = '{day}'")
            for cl in self.tables[2].get_all():
                sti = time.index(cl['start_time'])
                eti = time.index(cl['end_time'])
                for t in time[sti:eti+1]:
                    current_value = self.tables[9].get(t)[day]
                    if current_value == '-': current_value = ''
                    else: current_value +='\n'
                    current_value += cl['subject'] + ' ' + cl['level']+ ' '+ cl['year']
                    self.tables[9].update({day:current_value}, time.index(t))
        self.tables[2].setFilter(None)
    

class FindById(QWidget):
    signal = pyqtSignal(str)
    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_cam_widget()
        self.ui.setupUi(self) 

        # Create a QTimer to periodically update the video feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.ui.change_cam_button.clicked.connect(self.handle_cam_change)
        self.cam_list = None
        self.capture = None

    def show(self):
        super().show()
        if not self.cam_list:
                self.cam_list = self.get_available_cameras()
                self.cam_index = 0
        if len(self.cam_list) == 0:
            return
        self.capture = cv2.VideoCapture(self.cam_list[0])  
        self.timer.start(30)

    def handle_cam_change(self):
        self.capture.release()
        self.timer.stop()
        self.cam_index += 1
        if self.cam_index == len(self.cam_list):
            self.cam_index = 0
            self.capture = cv2.VideoCapture(self.cam_list[self.cam_index])
        else: self.capture = cv2.VideoCapture(self.cam_list[self.cam_index])
        self.timer.start()
    def get_available_cameras(self):
        available_cameras = []
        index = 0
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.isOpened():
                break
            ret, _ = cap.read()
            if ret:
                available_cameras.append(index)
                cap.release()
            index += 1
        return available_cameras

    
    def update_frame(self):
        # Read a frame from the camera
        ret, frame = self.capture.read()
        if ret:
            # Convert the OpenCV frame to QImage
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # Scale the QImage to fit the QLabel dimensions
            scaled_image = qt_image.scaled(self.ui.camera_label.width(), self.ui.camera_label.height())

            # Set the scaled QImage as the pixmap for the QLabel
            self.ui.camera_label.setPixmap(QPixmap.fromImage(scaled_image))

            # Convert the frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # # Apply image thresholding
            # _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
            #         # Detect QR codes in the grayscale image
            qr_codes = pyzbar.decode(gray)

            # Process each detected QR code
            for qr_code in qr_codes:
                # Extract the data from the QR code
                data = qr_code.data.decode('utf-8')
                self.signal.emit(data)
                self.capture.release()
                self.close()
    def closeEvent(self, e) -> None:
        self.capture.release()
        return super().closeEvent(e)


from PyQt5.QtWidgets import QStyledItemDelegate

class AlternateRowDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        if index.row() % 2 == 0:
            option.backgroundBrush = QtGui.QBrush(QtGui.QColor("#3D3846"))
