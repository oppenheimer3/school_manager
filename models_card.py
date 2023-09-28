from PyQt5.QtCore import  QTimer, Qt
from PyQt5.QtWidgets import QWidget, QLabel
from UI.PY.class_card import Ui_classCard
from UI.PY.teacher_card import Ui_TeacherCard
from UI.PY.student_card import Ui_StudentCard
import datetime
from PyQt5.QtGui import QImage, QPixmap
import cv2
from data_base import RegistrationTable
from pyzbar import pyzbar
import uuid
import qrcode
from subprocess import run
import platform
import base64
from bill import create_bill, open_pdf, create_pdf



def get_class_dates(day):
    days_lst = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    today = datetime.date.today()
    current_year = today.year
    next_year = current_year + 1

    start_date = datetime.date(current_year, 8, 1)
    end_date = datetime.date(next_year, 7, 31)

    dates = []
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() == days_lst.index(day):
            dates.append(current_date)
        current_date += datetime.timedelta(days=1)

    return dates




class TeacherCard(QWidget):
    def __init__(self, tables):
        super().__init__()
        self.ui_teacherCard = Ui_TeacherCard()
        self.ui_teacherCard.setupUi(self)
        self.tables = tables
        self.ui_teacherCard.tableView.setModel(self.tables[2])
        [self.ui_teacherCard.tableView.setColumnHidden(i, True) for i in [0, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]]

        #connect button
        self.ui_teacherCard.return_button.clicked.connect(lambda: self.ui_teacherCard.info_stacked_widget.setCurrentWidget(self.ui_teacherCard.info_widget))
        self.ui_teacherCard.payement_button.clicked.connect(self.handle_payement)
        self.ui_teacherCard.bill_button.clicked.connect(self.handle_bill)
        # set models
        self.tables[11].delete_all()
        self.ui_teacherCard.teacher_payement_tableview.setModel(self.tables[11])
        self.ui_teacherCard.teacher_payement_tableview.setColumnHidden(0, True) 

    def show(self,cl):
        super().show()
        self.ui_teacherCard.info_stacked_widget.setCurrentWidget(self.ui_teacherCard.info_widget)
        self.cl = cl
        self.tables[2].setFilter(f"teacher_id = '{self.cl['id']}'")
        if self.ui_teacherCard.info_layout.count() > 0:
            while self.ui_teacherCard.info_layout.count():
                item = self.ui_teacherCard.info_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    self.ui_teacherCard.info_layout.removeWidget(widget)
                    widget.deleteLater()
            while self.ui_teacherCard.labels_layout.count():
                item = self.ui_teacherCard.labels_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    self.ui_teacherCard.labels_layout.removeWidget(widget)
                    widget.deleteLater()
        for key, value in cl.items():
            if key == 'id': continue
            self.ui_teacherCard.labels_layout.addWidget(QLabel(f'{key}:'))
            self.ui_teacherCard.info_layout.addWidget(QLabel(str(value)))

    def handle_payement(self):
        self.tables[11].delete_all()
        classes = self.tables[2].get_all()
        for cl in classes:
            self.tables[3].setFilter(f"class_id = '{cl['id']}'")
            class_students = self.tables[3].get_all()
            class_salary = 0
            student_number = 0
            paid_student = 0
            for cl_student in class_students:
                self.tables[10].setFilter(f"class_student_id = '{cl_student['id']}' AND month = '{str(datetime.date.today().strftime('%m'))}'")
                student_pay = self.tables[10].get_all()
                if all(i['status'] == 'paid' for i in student_pay) and len(student_pay) != 0:
                    class_salary += float(cl['salary'])
                    paid_student += 1
                student_number += 1
            if cl['teacher_payement'] == 'by student':
                self.tables[11].add(cl['id'], str(student_number), str(paid_student), str(class_salary) )
            else:
                self.tables[11].add(cl['id'], str(student_number), str(paid_student), cl['salary'] )
        self.total = sum([float(i['class_salary']) for i in self.tables[11].get_all()])
        self.ui_teacherCard.total_label.setText(str(self.total))
        self.ui_teacherCard.info_stacked_widget.setCurrentWidget(self.ui_teacherCard.payement_widget)

    def handle_bill(self):
        self.tables[13].add(str(uuid.uuid4()), datetime.datetime.now().strftime('%Y-%m-%d'), self.cl['id'], '-' + str(self.total), 'teacher', datetime.datetime.now().strftime('%B'))
        if self.ui_teacherCard.generate_bill_checkbox.isChecked():
            pdf_file_path = "bill.pdf"
            bill_data = self.tables[11].get_all()
            for i, item in enumerate(bill_data):
                item['class_id']= i

            # Create the bill as a PDF
            create_bill(pdf_file_path, bill_data, self.total)
            # Open the PDF
            open_pdf(pdf_file_path)

    def closeEvent(self, event):
        # Custom code to run when the widget is closed
        self.tables[2].setFilter('')
        super().closeEvent(event)
        
class StudentCard(QWidget):
    def __init__(self, tables):
        super().__init__()
        self.ui_studentCard = Ui_StudentCard()
        self.ui_studentCard.setupUi(self)
        self.tables = tables
        #set model to tables
        self.ui_studentCard.student_class_table.setModel(self.tables[3])
        self.ui_studentCard.classes_table.setModel(self.tables[2])
        self.ui_studentCard.class_payement_tableview.setModel(self.tables[10])
        # enable buttons on selection
        self.ui_studentCard.student_class_table.selectionModel().selectionChanged.connect(lambda: (self.ui_studentCard.add_class_button.setEnabled(True), self.ui_studentCard.delete_class_button.setEnabled(True), self.ui_studentCard.class_payement_button.setEnabled(True)))
        self.ui_studentCard.classes_table.selectionModel().selectionChanged.connect(lambda: (self.ui_studentCard.ok_button.setEnabled(True), self.ui_studentCard.class_payement_button.setEnabled(True)))
        self.ui_studentCard.class_payement_tableview.selectionModel().selectionChanged.connect(lambda: self.ui_studentCard.update_button.setEnabled(True))
        ### hide columns
        [self.ui_studentCard.student_class_table.setColumnHidden(i,True) for i in [0, 1, 2, 3, 6, 7]]
        [self.ui_studentCard.classes_table.setColumnHidden(i,True) for i in [0, 1, 2, 5, 9]]

        # connect buttons
        self.ui_studentCard.add_class_button.clicked.connect(lambda: self.ui_studentCard.info_stacked_widget.setCurrentWidget(self.ui_studentCard.add_class_widget))
        self.ui_studentCard.delete_class_button.clicked.connect(lambda: (self.tables[3].delete(self.tables[3].selectedRecord(self.ui_studentCard.student_class_table)['id']), self.ui_studentCard.delete_class_button.setEnabled(False), self.ui_studentCard.class_payement_button.setEnabled(False)))
        self.ui_studentCard.cancel_button.clicked.connect(lambda: self.ui_studentCard.info_stacked_widget.setCurrentWidget(self.ui_studentCard.info_widget))
        self.ui_studentCard.ok_button.clicked.connect(self.add_class)
        self.ui_studentCard.search_button.clicked.connect(self.handle_search)
        self.ui_studentCard.view_button.clicked.connect(self.view_image)
        self.ui_studentCard.class_payement_button.clicked.connect(self.handle_class_payement)
        self.ui_studentCard.return_button.clicked.connect(lambda: (self.ui_studentCard.info_stacked_widget.setCurrentWidget(self.ui_studentCard.info_widget), self.ui_studentCard.update_button.setEnabled(False)) )
        self.ui_studentCard.update_payement_button.clicked.connect(lambda: (self.ui_studentCard.payement_stackedWidget.setCurrentWidget(self.ui_studentCard.page_2)))
        self.ui_studentCard.update_button.clicked.connect(self.update_payement)
        self.ui_studentCard.cancelupdate_button.clicked.connect(lambda: self.ui_studentCard.payement_stackedWidget.setCurrentWidget(self.ui_studentCard.page))

        # connect check boxes
        self.ui_studentCard.by_month.clicked.connect(self.show_month_table)
        self.ui_studentCard.by_session.clicked.connect(self.show_day_table)

        self.ui_studentCard.tabs.tabBarClicked.connect(self.tab_clicked )
    def tab_clicked(self, i):
        if i == 1:
            self.ui_studentCard.info_stacked_widget.setCurrentWidget(self.ui_studentCard.info_widget)
    

        
    def show_month_table(self):
        if self.tables[10].query.exec(f"SELECT * FROM ClassPayement WHERE class_student_id = '{self.class_student['id']}' GROUP BY year, month;"):
            self.tables[10].setQuery(self.tables[10].query)
        [self.ui_studentCard.class_payement_tableview.setColumnHidden(i,True) for i in [0, 1, 4, 5]]
        [self.ui_studentCard.class_payement_tableview.setColumnHidden(i,False) for i in [ 2, 3, 6]]

    def show_day_table(self):
        if self.tables[10].query.exec(f"SELECT * FROM ClassPayement WHERE class_student_id = '{self.class_student['id']}';"):
            self.tables[10].setQuery(self.tables[10].query)
        [self.ui_studentCard.class_payement_tableview.setColumnHidden(i,True) for i in [0, 1, 2, 3, 6]]
        [self.ui_studentCard.class_payement_tableview.setColumnHidden(i,False) for i in [ 4, 5]]

    def handle_class_payement(self):
        self.ui_studentCard.payement_stackedWidget.setCurrentWidget(self.ui_studentCard.page)
        self.class_student = self.tables[3].selectedRecord(self.ui_studentCard.student_class_table)
        class_date = self.tables[2].get(self.class_student['class_id'])['day']
        self.tables[10].setFilter(f" class_student_id = '{self.class_student['id']}'")
        self.tables[10].select()
        if self.tables[10].rowCount() == 0:
            for date in get_class_dates(class_date):
                id = str(uuid.uuid4())
                self.tables[10].add(id, self.class_student['id'], date.strftime("%m"), date.strftime("%Y"), date.strftime("%Y-%m-%d"), '-', '-')
        if self.tables[10].record(self.tables[10].rowCount()-1).value("year") == str(datetime.date.today().year):
            for date in get_class_dates(class_date):
                id = str(uuid.uuid4())
                self.tables[10].add(id, self.class_student['id'], date.strftime("%m"), date.strftime("%Y"), date.strftime("%Y-%m-%d"), '-', '-')
        if self.tables[10].query.exec(f"SELECT * FROM ClassPayement WHERE class_student_id = '{self.class_student['id']}' GROUP BY year, month;"):
            self.tables[10].setQuery(self.tables[10].query)

        [self.ui_studentCard.class_payement_tableview.setColumnHidden(i,True) for i in [0, 1, 4, 5]]
        self.ui_studentCard.info_stacked_widget.setCurrentWidget(self.ui_studentCard.class_payement_widget)
    def update_payement(self):
        if self.ui_studentCard.value_input.text() == '':
            return
        i = self.ui_studentCard.class_payement_tableview.selectionModel().currentIndex().row()
        class_payement = self.tables[10].selectedRecord(self.ui_studentCard.class_payement_tableview)
        class_ = self.tables[2].get(self.tables[3].get(class_payement['class_student_id'])['class_id'])
        class_price = float(class_['price'])
        session_price = float(class_['session_price'])

        self.tables[3].setFilter(f"student_id = '{self.cl['id']}'")
        input_value = float(self.ui_studentCard.value_input.text())
        diff = input_value - class_price
        diff_2 = input_value - session_price
        if self.ui_studentCard.by_session.isChecked():
            if diff_2 < 0:
                self.tables[10].update({"status":f"{diff_2}"}, i)
            else:
                self.tables[10].update({"status":"paid"}, i)
            sessions_month_num = self.tables[10].number_of_records({"class_student_id":f"{class_payement['class_student_id']}", "month": f"{class_payement['month']}"})
            sessions_month = self.tables[10].get_all()
            cur_pay = 0
            for s in sessions_month:
                if s['status'] == 'paid': cur_pay += session_price 
                elif s['status'] == '-': continue
                else: cur_pay += float(s['status']) + session_price
            diff_3 = cur_pay - session_price * sessions_month_num
            self.tables[10].update({"month_payement": f"{diff_3}" }, 0)
            if self.ui_studentCard.generate_bill_checkbox.isChecked():
                create_pdf('example.pdf',[datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), f"class: {class_['subject']+ ' ' + class_['year'] + class_['level']}", f"teacher: {class_['teacher']}", f"session date: {class_payement['date']}", f"session price: {session_price} DA", f"payement: {input_value}"]) 
                open_pdf('example.pdf')


        elif self.ui_studentCard.by_month.isChecked():
            if diff < 0:
                self.tables[10].update({"month_payement": f"{diff}" }, i)
            else:
                self.tables[10].update({"month_payement": "paid"}, i)
                query = f"UPDATE {self.tables[10].name} "
                query += f"SET status = 'paid' "
                query += f"WHERE month = '{class_payement['month']}' AND "
                query += f"class_student_id = '{class_payement['class_student_id']}'"
                if not self.tables[10].query.exec(query):
                    print('failed to execute')
            if self.ui_studentCard.generate_bill_checkbox.isChecked():
                create_pdf('example.pdf',[datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), f"class: {class_['subject']+ ' ' + class_['year'] + class_['level']}", f"teacher: {class_['teacher']}", f"month: {class_payement['month']}", f"class price: {class_price} DA", f"payement: {input_value} DA"]) 
                open_pdf('example.pdf')
        self.ui_studentCard.update_button.setEnabled(False)
        self.tables[13].add(str(uuid.uuid4()), datetime.datetime.now().strftime('%Y-%m-%d'), self.cl['id'], str(input_value), 'student', datetime.datetime.now().strftime('%B'))
        self.ui_studentCard.payement_stackedWidget.setCurrentWidget(self.ui_studentCard.page)
                

            

    def view_image(self):
        self.generate_qr_code(self.cl['id'])
        if platform.system()=='Linux':
            run(['xdg-open', 'qr_code.png'])  
        else: run(['start', '', 'qr_code.png'], shell=True)

    def generate_qr_code(self, data):
        qr = qrcode.QRCode()
        qr.add_data(data)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_image.save('qr_code.png', "PNG")
    
    def show(self,cl):
        super().show()
        self.ui_studentCard.info_stacked_widget.setCurrentWidget(self.ui_studentCard.info_widget)
        self.ui_studentCard.payement_stackedWidget.setCurrentWidget(self.ui_studentCard.page)
        self.ui_studentCard.class_payement_button.setEnabled(False)
        self.cl = cl
        self.tables[3].setFilter(f"student_id = '{self.cl['id']}'")
        if self.ui_studentCard.info_layout.count() > 0:
            while self.ui_studentCard.info_layout.count():
                item = self.ui_studentCard.info_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    self.ui_studentCard.info_layout.removeWidget(widget)
                    widget.deleteLater()
            while self.ui_studentCard.labels_layout.count():
                item = self.ui_studentCard.labels_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    self.ui_studentCard.labels_layout.removeWidget(widget)
                    widget.deleteLater()
            
        for key, value in cl.items():
            if key == 'id' or key == "photo": continue
            self.ui_studentCard.labels_layout.addWidget(QLabel(f'{key}:'))
            self.ui_studentCard.info_layout.addWidget(QLabel(str(value)))
        # self.ui_studentCard.qr_code_label.setPixmap(QPixmap.fromImage(QImage.fromData(base64.b64decode(self.tables[1].selectedRecord()['photo']))))
        image_data = base64.b64decode(self.tables[1].selectedRecord()['photo'])
        image = QImage.fromData(image_data)
        pixmap = QPixmap.fromImage(image)
        label_size = self.ui_studentCard.qr_code_label.size()
        scaled_pixmap = pixmap.scaled(label_size, aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        self.ui_studentCard.qr_code_label.setPixmap(scaled_pixmap)

    def add_class(self):
        id = str(uuid.uuid4())
        student_name = self.cl['first_name'] + ' ' + self.cl['last_name']
        student_id = self.cl['id']
        class_fields =  self.tables[2].selectedRecord(self.ui_studentCard.classes_table)
        #self.tables[3].setFilter(None)         
        self.tables[3].add(id, student_name, class_fields['level'], class_fields['year'], class_fields['subject'], class_fields['teacher'], student_id, class_fields['id'] )
        # self.tables[3].setFilter(f"student_id = '{self.cl['id']}'")
        self.ui_studentCard.info_stacked_widget.setCurrentWidget(self.ui_studentCard.info_widget)
        self.ui_studentCard.class_payement_button.setEnabled(False)

    def handle_search(self):
        search_input = self.ui_studentCard.search_input.text()
        self.tables[2].search(self.tables[2].fields.keys(), search_input)

    def closeEvent(self, event):
        # Custom code to run when the widget is closed
        self.tables[3].setFilter('')
        super().closeEvent(event)

class ClassCard(QWidget):
    def __init__(self, tables):
        super().__init__()
        self.ui_classCard = Ui_classCard()
        self.ui_classCard.setupUi(self)
        self.tables = tables
        self.ui_classCard.calendarWidget.selectionChanged.connect(lambda: self.handle_date_change(self.ui_classCard.calendarWidget.selectedDate()))
        self.RegistrationTable = RegistrationTable(self.ui_classCard.registration_table)
        # Open the camera
        self.detector = cv2.QRCodeDetector()
        self.cam_list = None
        self.capture = None

        # Create a QTimer to periodically update the video feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        #set models to table views
        self.ui_classCard.student_table.setModel(self.tables[1])
        self.ui_classCard.classstudents_table.setModel(self.tables[3])
        self.ui_classCard.record_table.setModel(self.tables[6])
        self.ui_classCard.attendance_table.setModel(self.tables[7])
        self.ui_classCard.payement_tableview.setModel(self.tables[10])
        ## hide certain fields
        [self.ui_classCard.attendance_table.setColumnHidden(i,True) for i in [0, 3, 4]]
        [self.ui_classCard.classstudents_table.setColumnHidden(i,True) for i in [0, 2, 3, 4, 5, 6, 7]]
        [self.ui_classCard.student_table.setColumnHidden(i, True) for i in [0, 5]]
        [self.ui_classCard.record_table.setColumnHidden(i, True) for i in [0,1]]
        [self.ui_classCard.payement_tableview.setColumnHidden(i,True) for i in [0, 1, 2]]
        #connect buttons
        self.ui_classCard.tabs.tabBarClicked.connect(self.tab_clicked )
        self.ui_classCard.cancel_button.clicked.connect(lambda: self.ui_classCard.class_student_stackedwidget.setCurrentWidget(self.ui_classCard.class_students_widget))
        self.ui_classCard.add_student_button.clicked.connect(lambda: self.ui_classCard.class_student_stackedwidget.setCurrentWidget(self.ui_classCard.add_student_widget))
        self.ui_classCard.delete_student_button.clicked.connect(lambda: self.tables[3].delete(self.tables[3].selectedRecord(self.ui_classCard.classstudents_table)['id']))
        self.ui_classCard.ok_button.clicked.connect(self.add_student_to_class)
        self.ui_classCard.search_button.clicked.connect(self.find_student)
        self.ui_classCard.delete_record_button.clicked.connect(lambda: (self.tables[6].delete(self.tables[6].selectedRecord(self.ui_classCard.record_table)['id']), self.ui_classCard.delete_record_button.setEnabled(False), self.ui_classCard.Attendance_button.setEnabled(False)))
        self.ui_classCard.register_attendance_button.clicked.connect(self.handle_registration)
        self.ui_classCard.stop_registration_button.clicked.connect(lambda: (self.ui_classCard.info_stacked_widget.setCurrentWidget(self.ui_classCard.info_widget), self.timer.stop(), self.capture.release()))
        self.ui_classCard.Attendance_button.clicked.connect(lambda: (self.ui_classCard.records_stackedwidget.setCurrentWidget(self.ui_classCard.attendance_widget), self.tables[7].setFilter(f"class_record_id = '{self.tables[6].selectedRecord(self.ui_classCard.record_table)['id']}'")))
        self.ui_classCard.return_button.clicked.connect(lambda: self.ui_classCard.records_stackedwidget.setCurrentWidget(self.ui_classCard.record_widget))
        self.ui_classCard.change_cam_button.clicked.connect(self.handle_cam_change)
        self.ui_classCard.delete_all_button.clicked.connect(lambda: (self.tables[6].delete_all(), self.ui_classCard.delete_record_button.setEnabled(False), self.ui_classCard.Attendance_button.setEnabled(False)))
        self.ui_classCard.payement_button.clicked.connect(lambda: (self.ui_classCard.class_student_stackedwidget.setCurrentWidget(self.ui_classCard.payement_widget), self.tables[10].setFilter(f"class_student_id = '{self.tables[3].selectedRecord(self.ui_classCard.classstudents_table)['id']}' ")))
        self.ui_classCard.return_button_2.clicked.connect(lambda: self.ui_classCard.class_student_stackedwidget.setCurrentWidget(self.ui_classCard.class_students_widget))
        self.ui_classCard.paid_students_button.clicked.connect(self.handel_paid_student)
        self.ui_classCard.unpaid_students_button.clicked.connect(self.handel_unpaid_student)
        self.ui_classCard.show_all_button.clicked.connect(lambda: self.tables[3].setFilter(f" class_id = '{self.cl['id']}'"))
        #onchange selection connection
        self.ui_classCard.student_table.selectionModel().selectionChanged.connect(lambda: (self.ui_classCard.ok_button.setEnabled(True)))
        self.ui_classCard.classstudents_table.selectionModel().selectionChanged.connect(lambda: (self.ui_classCard.delete_student_button.setEnabled(True), self.ui_classCard.payement_button.setEnabled(True)))
        self.ui_classCard.record_table.selectionModel().selectionChanged.connect(lambda: (self.ui_classCard.Attendance_button.setEnabled(True), self.ui_classCard.delete_record_button.setEnabled(True)))




    def show(self, cl):
        super().show()
        self.ui_classCard.info_stacked_widget.setCurrentWidget(self.ui_classCard.info_widget)
        self.ui_classCard.class_student_stackedwidget.setCurrentWidget(self.ui_classCard.class_students_widget)
        self.ui_classCard.records_stackedwidget.setCurrentWidget(self.ui_classCard.record_widget)
        self.ui_classCard.tabs.setCurrentIndex(0)
        self.cl = cl
        self.tables[6].setFilter(f"class_id = '{self.cl['id']}'")
        self.tables[3].setFilter(f"class_id = '{self.cl['id']}'")
        self.tables[3].select()
        if self.ui_classCard.info_layout.count() > 0:
            while self.ui_classCard.info_layout.count():
                item = self.ui_classCard.info_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    self.ui_classCard.info_layout.removeWidget(widget)
                    widget.deleteLater()
            while self.ui_classCard.labels_layout.count():
                item = self.ui_classCard.labels_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    self.ui_classCard.labels_layout.removeWidget(widget)
                    widget.deleteLater()
        for key, value in cl.items():
            if key == 'id' or key == 'teacher_id':
                continue
            self.ui_classCard.labels_layout.addWidget(QLabel(f'{key}:'))
            self.ui_classCard.info_layout.addWidget(QLabel(str(value)))  
                
    def add_student_to_class(self):
        class_student_id = str(uuid.uuid4())
        student = self.tables[1].selectedRecord(self.ui_classCard.student_table)
        self.tables[3].add(class_student_id, student['first_name']+' '+student['last_name'], self.cl['level'], self.cl['year'], self.cl['subject'], self.cl['teacher'], student['id'], self.cl['id'])
        self.ui_classCard.class_student_stackedwidget.setCurrentWidget(self.ui_classCard.class_students_widget)

    def find_student(self):
        search_str = self.ui_classCard.search_input.text()
        self.tables[1].search(['first_name','last_name'], search_str)


    def handle_registration(self):
        if not self.cam_list:
                self.cam_list = self.get_available_cameras()
                self.cam_index = 0
        if len(self.cam_list) == 0:
            return
        self.capture = cv2.VideoCapture(self.cam_list[0])  
        id = str(uuid.uuid4())
        self.tables[6].add(id, self.cl['id'], datetime.date.today().strftime("%Y-%m-%d"))
        self.ui_classCard.info_stacked_widget.setCurrentWidget(self.ui_classCard.camera_widget)
        self.RegistrationTable.delete_all()
        self.timer.start(30)  # Set the desired update interval in milliseconds

    
    def handle_date_change(self,date):
        self.tables[6].setFilter(f"class_date = '{date.toString('yyyy-MM-dd')}'")

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
            scaled_image = qt_image.scaled(self.ui_classCard.video_label.width(), self.ui_classCard.video_label.height())

            # Set the scaled QImage as the pixmap for the QLabel
            self.ui_classCard.video_label.setPixmap(QPixmap.fromImage(scaled_image))

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

            # # Detect and decode QR codes in the thresholded image
            # decoded_data, points, _ = self.detector.detectAndDecode(thresh)
            # # Check if a QR code is detected
            # if points is None or not decoded_data:
            #     return
                self.tables[3].setFilter(f"class_id = '{self.cl['id']}' AND student_id = '{data}'")
                student = {i:self.tables[3].record(0).value(i) for i in self.tables[3].fields.keys()}
                self.tables[10].setFilter(f"class_student_id = '{student['id']}' AND date = '{datetime.date.today().strftime('%Y-%m-%d')}'")
                attended = self.RegistrationTable.get(student['student_id'])
                if student['student_id'] and not attended['id']:
                    self.RegistrationTable.add(student['student_id'], student['name'], self.tables[10].record(0).value('status'))
                    id = str(uuid.uuid4())
                    record_id = self.tables[6].record(self.tables[6].rowCount()-1).value('id')
                    self.tables[7].add(id, student['name'], datetime.datetime.now().strftime("%H:%M:%S"),student['student_id'], record_id)
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
    
    def tab_clicked(self, i):
        if i==1: self.ui_classCard.class_student_stackedwidget.setCurrentWidget(self.ui_classCard.class_students_widget)
        elif i==2: self.ui_classCard.records_stackedwidget.setCurrentWidget(self.ui_classCard.record_widget)

    def handel_paid_student(self):
        paid_query = """
                SELECT ClassStudents.*
                FROM ClassStudents
                INNER JOIN Classes ON ClassStudents.class_id = Classes.id 
                INNER JOIN ClassPayement ON ClassStudents.id = ClassPayement.class_student_id
                """
        paid_query += f" WHERE month = '{str(datetime.date.today().strftime('%m'))}' AND "
        paid_query += f" class_id = '{self.cl['id']}' AND "
        paid_query += f" month_payement = 'paid'; "
        # paid_query += "GROUP BY ClassPayement.year, ClassPayement.month, ClassPayement.class_student_id"


        if self.tables[3].query.exec(paid_query):
            self.tables[3].setQuery(self.tables[3].query)
    def handel_unpaid_student(self):
        paid_query = """
            SELECT DISTINCT ClassStudents.*
            FROM ClassStudents
            INNER JOIN ClassPayement ON ClassStudents.id = ClassPayement.class_student_id
        """
        paid_query += f" WHERE month = '{str(datetime.date.today().strftime('%m'))}' AND "
        paid_query += f" class_id = '{self.cl['id']}' AND "
        paid_query += """
            NOT EXISTS (
                SELECT 1
                FROM ClassPayement
                WHERE ClassStudents.id = ClassPayement.class_student_id
                AND month_payement = 'paid'
            );
            """

        if self.tables[3].query.exec(paid_query):
            self.tables[3].setQuery(self.tables[3].query)


    def closeEvent(self, event):
        # Custom code to run when the widget is closed
        self.tables[1].setFilter('')
        if self.capture: self.capture.release()
        super().closeEvent(event)