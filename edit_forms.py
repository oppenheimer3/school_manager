import typing
from PyQt5 import QtCore
from UI.PY.class_edit_form import Ui_class_edit_form
from UI.PY.teacher_edit_form import Ui_teacher_edit_form
from UI.PY.student_edit_form import Ui_student_edit_form
from UI.PY.user_edit_form import Ui_edit_user_form
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTime



class EditClassForm(QWidget):
    def __init__(self, tables):
        super().__init__()
        self.ui = Ui_class_edit_form()
        self.ui.setupUi(self)
        self.ui.Cancel_button.clicked.connect(lambda: self.close())
        self.tables = tables
        # fill the combobox
        self.input_fields = [self.ui.level_combobox,self.ui.teacher_combobox, self.ui.day_combobox, self.ui.subject_combobox, self.ui.year_combobox, self.ui.classroom_combobox, self.ui.teachers_payement_combobox]


        #connect on selection change
        self.ui.level_combobox.currentIndexChanged.connect(self.handle_level_change)
        self.ui.subject_combobox.currentIndexChanged.connect(self.handle_subject_change)

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

    def show(self, cl):
        super().show()
        [i.clear() for i in self.input_fields]
        self.ui.level_combobox.addItems(['Elementry school', 'Middle school', 'High school'])
        self.ui.teachers_payement_combobox.addItems(['fixed salary', 'by student'])
        self.handle_subject_change(0)
        self.ui.day_combobox.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        self.ui.subject_combobox.addItems([i['subject_name'] for i in self.tables[4].get_all()])
        # self.ui.year_combobox.addItems(['1', '2', '3', '4', '5'])
        self.ui.classroom_combobox.addItems([i['classroom_name'] for i in self.tables[5].get_all()])
        self.cl = cl
        self.ui.level_combobox.setCurrentText(self.cl['level'])
        self.ui.teacher_combobox.setCurrentText(self.cl['teacher'])
        self.ui.day_combobox.setCurrentText(self.cl['day'])
        self.ui.subject_combobox.setCurrentText(self.cl['subject'])
        self.ui.year_combobox.setCurrentText(self.cl['year'])
        self.ui.start_time_input.setTime(QTime.fromString(self.cl['start_time']))
        self.ui.end_time_input.setTime(QTime.fromString(self.cl['end_time']))
        self.ui.price_input.setText(self.cl['price'])
        self.ui.session_price_input.setText(self.cl['session_price'])
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


        


class EditTeacherForm(QWidget):
    def __init__(self, tables):
        super().__init__()
        self.ui = Ui_teacher_edit_form()
        self.ui.setupUi(self)
        self.ui.Cancel_button.clicked.connect(lambda: self.close())
        self.tables = tables
    def show(self, cl):
        super().show()
        self.ui.subject_comboBox.clear()
        self.ui.subject_comboBox.addItems([i['subject_name'] for i in self.tables[4].get_all()])
        self.ui.level_combobox.clear()
        self.ui.level_combobox.addItems(['Elementry school', 'Middle school', 'High school'])
        self.cl = cl
        self.ui.firstname_input.setText(self.cl['first_name'])
        self.ui.lastname_input.setText(self.cl['last_name'])
        self.ui.subject_comboBox.setCurrentText(self.cl['subject'])
    def get_data(self):
        return {
            'first_name': self.ui.firstname_input.text(),
            'last_name': self.ui.lastname_input.text(),
            'phone': self.ui.phone_input.text(),
            'email': self.ui.email_input.text(),
            'subject': self.ui.subject_comboBox.currentText(),
            'level': self.ui.level_combobox.currentText()
        }


class EditStudentForm(QWidget):
    def __init__(self, tables):
        super().__init__()
        self.ui = Ui_student_edit_form()
        self.ui.setupUi(self)
        self.ui.Cancel_button.clicked.connect(lambda: self.close())
        self.tables = tables
    def show(self, cl):
        super().show()
        self.cl = cl
        self.ui.firstname_input.setText(self.cl['first_name'])
        self.ui.lastname_input.setText(self.cl['last_name'])
    def get_data(self):
        return{
            'first_name': self.ui.firstname_input.text(),
            'last_name': self.ui.lastname_input.text(),
            'phone': self.ui.phone_input.text(),
            'email': self.ui.email_input.text(),
        }


class EditUserForm(QWidget):
    def __init__(self, tables) -> None:
        super().__init__()
        self.tables = tables
        self.ui = Ui_edit_user_form()
        self.ui.setupUi(self)
        self.ui.cancel_button.clicked.connect(lambda: self.close())
        self.ui.save_button.clicked.connect(self.edit_user)
        self.ui.role_comboBox.addItems(['manager', 'employee'])

    def show(self, user, i):
        super().show()
        self.user = user
        self.ui.username_input.setText(user['username'])
        self.ui.role_comboBox.setCurrentText(user['role'])
        if i==0:
            self.ui.role_comboBox.setEnabled(False)


    def edit_user(self):
        username = self.ui.username_input.text()
        password = self.ui.password_input.text()
        cpassword = self.ui.password_input_2.text()
        role = self.ui.role_comboBox.currentText()
        if password == cpassword:
            self.tables[12].update({"username":username, "password": password, "role": role})
            self.close()
