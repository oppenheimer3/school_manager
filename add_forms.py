
from UI.PY.class_add_form import Ui_class_add_form
from UI.PY.teacher_add_form import Ui_teacher_add_form
from UI.PY.student_add_form import Ui_student_add_form
from UI.PY.user_add_form import Ui_add_user_form
from PyQt5.QtWidgets import QWidget
import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import  QTimer
import base64
from PyQt5.QtCore import QResource






class AddClassForm(QWidget):
    def __init__(self, tables):
        super().__init__()
        self.ui = Ui_class_add_form()
        self.ui.setupUi(self)
        self.tables = tables
        self.ui.Cancel_button.clicked.connect(lambda: self.close())
        self.input_fields = [self.ui.level_combobox,self.ui.teacher_combobox, self.ui.day_combobox, self.ui.subject_combobox, self.ui.year_combobox, self.ui.classroom_combobox, self.ui.teachers_payement_combobox]
        #connect on selection change
        self.ui.level_combobox.currentIndexChanged.connect(self.handle_level_change)
        self.ui.subject_combobox.currentIndexChanged.connect(self.handle_subject_change)
        self.ui.price_input.textChanged.connect(self.set_session_price)
    def set_session_price(self):
        try:
            self.ui.session_price_input.setText(str(float(self.ui.price_input.text())/4))
        except: return    
    def handle_level_change(self, i):
        self.ui.year_combobox.clear()
        self.ui.teacher_combobox.clear()
        self.tables[0].setFilter(f"subject = '{self.ui.subject_combobox.currentText()}' AND level = '{self.ui.level_combobox.currentText()}'")
        self.tables[0].select()
        self.teachers = self.tables[0].get_all()
        self.ui.teacher_combobox.addItems([teacher['first_name'] + ' ' + teacher['last_name'] for teacher in self.teachers])
        if i==0:
            self.ui.year_combobox.addItems(['1', '2', '3', '4', '5'])
        elif i==1:
            self.ui.year_combobox.addItems(['1', '2', '3', '4'])
        elif i==2:
            self.ui.year_combobox.addItems(['1', '2', '3'])
    def handle_subject_change(self, i):
        self.ui.teacher_combobox.clear()
        self.tables[0].setFilter(f"subject = '{self.ui.subject_combobox.currentText()}' AND level = '{self.ui.level_combobox.currentText()}'")
        self.tables[0].select()
        self.teachers = self.tables[0].get_all()
        self.ui.teacher_combobox.addItems([teacher['first_name'] + ' ' + teacher['last_name'] for teacher in self.teachers])

    def show(self):
        super().show()
        [i.clear() for i in self.input_fields]
        # fill the combobox
        self.ui.level_combobox.addItems(['Elementry school', 'Middle school', 'High school'])
        self.ui.teachers_payement_combobox.addItems(['fixed salary', 'by student'])
        self.handle_subject_change(0)
        self.ui.day_combobox.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        self.ui.subject_combobox.addItems([i['subject_name'] for i in self.tables[4].get_all()])
        self.ui.classroom_combobox.addItems([i['classroom_name'] for i in self.tables[5].get_all()])
        
    def get_data(self):
        return {
            'level':self.ui.level_combobox.currentText(), 
            'year':self.ui.year_combobox.currentText(), 
            'subject': self.ui.subject_combobox.currentText(), 
            'teacher': self.ui.teacher_combobox.currentText(),
            'classroom': self.ui.classroom_combobox.currentText(),
            'day': self.ui.day_combobox.currentText(),
            'start_time': self.ui.start_time_input.time().toString("hh:mm"),
            'end_time': self.ui.end_time_input.time().toString("hh:mm"),
            'teacher_id': (
                self.teachers[self.ui.teacher_combobox.currentIndex()]['id']
                if len(self.teachers) > 0 else '-'
            ),
            'price': self.ui.price_input.text(),
            'session_price': self.ui.session_price_input.text(), 
            'teacher_payement':self.ui.teachers_payement_combobox.currentText(),
            'salary':self.ui.salary_input.text()
        }
    

class AddTeacherForm(QWidget):
    def __init__(self, tables):
        super().__init__()
        self.ui = Ui_teacher_add_form()
        self.ui.setupUi(self)
        self.ui.Cancel_button.clicked.connect(lambda: self.close())
        self.tables = tables
    def show(self):
        super().show()
        self.ui.subject_comboBox.clear()
        self.ui.subject_comboBox.addItems([i['subject_name'] for i in self.tables[4].get_all()])
        self.ui.level_combobox.clear()
        self.ui.level_combobox.addItems(['Elementry school', 'Middle school', 'High school'])
    def get_data(self):
        return {
            'first_name': self.ui.firstname_input.text(),
            'last_name': self.ui.lastname_input.text(),
            'phone': self.ui.phone_input.text(),
            'email': self.ui.email_input.text(),
            'subject': self.ui.subject_comboBox.currentText(),
            'level': self.ui.level_combobox.currentText()
        }

class AddStudentForm(QWidget):
    def __init__(self, tables):
        super().__init__()
        self.ui = Ui_student_add_form()
        self.ui.setupUi(self)
        self.ui.Cancel_button.clicked.connect(lambda: self.close())
        self.ui.take_photo_button.clicked.connect(self.handle_take_photo)
        self.ui.take_button.clicked.connect(self.handle_take)
        self.tables = tables
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.takeClicked = False
        self.ui.change_cam_button.clicked.connect(self.handle_cam_change)
        self.ui.stackedWidget.setCurrentWidget(self.ui.page)
        self.cam_list = None
        self.capture = None
    def get_data(self):
        if self.takeClicked: 
            img = "student.png" 
            with open(img, "rb") as image_file:
                binary_data = image_file.read()
        else: 
            img = ":/icons/404.png"
            binary_data = QResource(img).data()
        base64_data = base64.b64encode(binary_data).decode("utf-8")

        return{
            'first_name': self.ui.firstname_input.text(),
            'last_name': self.ui.lastname_input.text(),
            'phone': self.ui.phone_input.text(),
            'email': self.ui.email_input.text(),
            'photo': base64_data
        }
    def handle_take(self):
        self.takeClicked = True
        self.ui.stackedWidget.setCurrentWidget(self.ui.page)
    def handle_take_photo(self):
        if not self.cam_list:
                self.cam_list = self.get_available_cameras()
                self.cam_index = 0
        if len(self.cam_list) == 0:
            return
        self.capture = cv2.VideoCapture(self.cam_list[0])  
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_2)
        self.timer.start(30)
    def update_frame(self):
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

            if self.takeClicked:
                qt_image.save('student.png')
                self.capture.release()
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
    

class AddUserForm(QWidget):
    def __init__(self, tables) -> None:
        super().__init__()
        self.tables = tables
        self.ui = Ui_add_user_form()
        self.ui.setupUi(self)
        self.ui.cancel_button.clicked.connect(lambda: self.close())
        self.ui.role_comboBox.addItems(['manager', 'employee'])
        self.ui.add_button.clicked.connect(self.add_user)
    def add_user(self):
        username = self.ui.username_input.text()
        password = self.ui.password_input.text()
        cpassword = self.ui.password_input_2.text()
        role = self.ui.role_comboBox.currentText()
        if password == cpassword:
            self.tables[12].add(username, password, role)
            self.close()