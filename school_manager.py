from PyQt5 import QtWidgets
from UI.PY.gui import Ui_MainWindow
from data_base import initialize_db ,Teachers, Students, Classes, ClassStudents, Subjects, Classrooms, ClassRecords, Attendance, ClassFilter, TimeManagement, ClassPayement, TeacherPayement, Users, Payment
import uuid
from side_widgets import LoginWindow, SubjectList, ClassroomList, AddClassFilter, ClickableLabel, TimeManagementWidget, FindById, AlternateRowDelegate
from add_forms import AddClassForm,  AddTeacherForm, AddStudentForm, AddUserForm
from edit_forms import EditTeacherForm, EditClassForm, EditStudentForm, EditUserForm
from models_card import ClassCard, TeacherCard, StudentCard
import datetime, calendar
import resources


class MY_MainWindow(QtWidgets.QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        delegate = AlternateRowDelegate()
        self.ui.classe_table.setItemDelegate(delegate)
        self.ui.teachers_table.setItemDelegate(delegate)
        self.ui.students_table.setItemDelegate(delegate)
        self.ui.payment_tableview.setItemDelegate(delegate)        
        self.ui.users_tableView.setItemDelegate(delegate)

        # database tables
        self.Teachers = Teachers(self.ui.teachers_table)
        self.Students = Students(self.ui.students_table)
        self.Classes = Classes(self.ui.classe_table)
        self.ClassStudents = ClassStudents()
        self.Subjects = Subjects()
        self.Classrooms = Classrooms()
        self.ClassRecords = ClassRecords()
        self.Attendance = Attendance()
        self.ClassFilter = ClassFilter(self.ui.filter_table)
        self.TimeManagement = TimeManagement()
        self.ClassPayement = ClassPayement()
        self.TeacherPayement = TeacherPayement()
        self.Users = Users(self.ui.users_tableView)
        self.Payment = Payment(self.ui.payment_tableview)
        self.ClassFilter.delete_all()
        self.tables = [self.Teachers, self.Students, self.Classes, self.ClassStudents, self.Subjects, self.Classrooms, self.ClassRecords, self.Attendance, self.ClassFilter, self.TimeManagement, self.ClassPayement, self.TeacherPayement, self.Users, self.Payment ]
        self.ui.teachers_table.selectionModel().selectionChanged.connect(lambda: (self.ui.delete_teacher_button.setEnabled(True), self.ui.edit_teacher_button.setEnabled(True), self.ui.open_teacher_button.setEnabled(True)))
        self.ui.students_table.selectionModel().selectionChanged.connect(lambda: (self.ui.delete_student_button.setEnabled(True), self.ui.edit_student_button.setEnabled(True), self.ui.open_student_button.setEnabled(True)))
        self.ui.classe_table.selectionModel().selectionChanged.connect(lambda: (self.ui.open_class_button.setEnabled(True),self.ui.delete_class_button.setEnabled(True), self.ui.edit_class_button.setEnabled(True)))
        self.ui.users_tableView.selectionModel().selectionChanged.connect(self.handle_selection_user_changed)
        self.ui.payment_tableview.selectionModel().selectionChanged.connect(lambda: self.ui.with_button.setEnabled(True))
        self.ui.tabs.tabBarClicked.connect(self.tab_clicked )

        #### hide columns
        self.Classes.hide_columns([0, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
        self.Teachers.hide_columns([0, 3, 4])
        self.Students.hide_columns([0, 5])
        self.Users.hide_columns([1,])
        self.Payment.hide_columns([0, 2, 5])


        # hide some fun for non managers
        if user['role'] != 'manager':
            self.ui.tabs.removeTab(3)
            self.ui.tabs.removeTab(3)


        # ##### create crud forms of the tables
        # # teacher crud formss
        self.TeachersAddForm = AddTeacherForm(self.tables)
        self.TeachersEditForm = EditTeacherForm(self.tables)
        # #student crud forms
        self.StudentsAddForm = AddStudentForm(self.tables)
        self.StudentsEditForm = EditStudentForm(self.tables)
        #class crud forms
        self.ClassAddForm = AddClassForm(self.tables)
        self.ClassEditForm = EditClassForm(self.tables)
        # users form
        self.UsersAddForm = AddUserForm(self.tables)
        self.UsersEditForm = EditUserForm(self.tables)

        #subjects list widget
        self.SubjectList = SubjectList(self.Subjects)
        #classroom list widger
        self.ClassroomList = ClassroomList(self.Classrooms)
        #add class filter
        self.AddClassFilter = AddClassFilter(self.tables)
        # time management widget
        self.TimeManagementWidget = TimeManagementWidget(self.tables)

        # find by id widget 
        self.FindById = FindById()

        ###### creaate Cards
        ## class card
        self.ClassCard = ClassCard(self.tables)
        # teacher card
        self.TeacherCard = TeacherCard(self.tables)
        # student card
        self.StudentCard = StudentCard(self.tables)
        
        #remove selection buttons
        self.teacher_buttons = [self.ui.open_teacher_button, self.ui.delete_teacher_button, self.ui.edit_teacher_button]
        self.student_buttons = [self.ui.open_student_button, self.ui.delete_student_button, self.ui.edit_student_button]
        self.class_buttons = [self.ui.open_class_button, self.ui.delete_class_button, self.ui.edit_class_button]

        #add some data to classroom and subjects
        if len(self.Subjects.get_all()) == 0:
            [self.Subjects.add(i) for i in ['Math', 'Physics', 'Biology']]
        if len(self.Classrooms.get_all()) == 0:
            [self.Classrooms.add(i) for i in ['Classroom 1', 'Classroom 2', 'Classroom 3', 'Classroom 4', 'Classroom 5', 'Classroom 6']] 


        # connect crud buttons
        self.ui.add_teacher_button.clicked.connect(lambda: self.TeachersAddForm.show())
        self.ui.add_student_button.clicked.connect(lambda: self.StudentsAddForm.show())
        self.ui.add_class_button.clicked.connect(lambda: self.ClassAddForm.show())
        self.ui.delete_teacher_button.clicked.connect(self.delete_teacher)
        self.ui.delete_student_button.clicked.connect(self.delete_student)
        self.ui.delete_class_button.clicked.connect(self.delete_class)
        self.ui.edit_teacher_button.clicked.connect(lambda: self.TeachersEditForm.show(self.Teachers.selectedRecord()))
        self.ui.edit_student_button.clicked.connect(lambda: self.StudentsEditForm.show(self.Students.selectedRecord()))
        self.ui.edit_class_button.clicked.connect(lambda: self.ClassEditForm.show(self.Classes.selectedRecord()))
        self.ui.open_class_button.clicked.connect(lambda: (self.ClassCard.show(self.Classes.selectedRecord()), self.clear_selection(self.class_buttons, self.ui.classe_table)))
        self.ui.open_teacher_button.clicked.connect(lambda: (self.TeacherCard.show(self.Teachers.selectedRecord()), self.clear_selection(self.teacher_buttons, self.ui.teachers_table)))
        self.ui.open_student_button.clicked.connect(lambda: (self.StudentCard.show(self.Students.selectedRecord()), self.clear_selection(self.student_buttons, self.ui.students_table)))
        self.ui.subjects_button.clicked.connect(lambda: self.SubjectList.show())
        self.ui.classroom_button.clicked.connect(lambda: self.ClassroomList.show())
        self.ui.filter_button.clicked.connect(lambda: self.AddClassFilter.show())
        self.ui.remove_filter_button.clicked.connect(self.remove_filter)
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.ui.today_classes_button.clicked.connect(lambda: self.Classes.setFilter(f'day = {self.days[datetime.datetime.now().weekday()]}'))
        self.ui.search_teacher_button.clicked.connect(lambda: self.Teachers.search(["first_name","last_name"], self.ui.search_teacher_input.text()))
        self.ui.teacher_reaturn_button.clicked.connect(lambda: self.ui.teacher_stackedwidget.setCurrentWidget(self.ui.teachers_list_widget))
        self.ui.info_teacher_button.clicked.connect(self.show_info)
        self.ui.show_all_button.clicked.connect(lambda: self.Teachers.setFilter(None))
        self.ui.search_student_button.clicked.connect(lambda: self.Students.search(["id", "first_name","last_name"], self.ui.search_student_input.text()))
        self.ui.time_management_button.clicked.connect(lambda: self.TimeManagementWidget.show())
        self.ui.delete_user_button.clicked.connect(lambda:(self.ui.delete_user_button, self.Users.delete(self.Users.selectedRecord()['username'])))
        self.ui.add_user_button.clicked.connect(lambda: self.UsersAddForm.show())
        self.ui.edit_user_button.clicked.connect(lambda: self.UsersEditForm.show(self.Users.selectedRecord(), self.ui.users_tableView.selectionModel().currentIndex().row()))
        self.ui.find_by_id_button.clicked.connect(lambda: self.FindById.show())
        self.FindById.signal.connect(lambda id: self.Students.setFilter(f"id = '{id}'"))
        self.ui.showall_payment_button.clicked.connect(lambda: (self.Payment.setFilter(None), self.ui.profit_label.setText(str(sum([float(i['amount']) for i in self.Payment.get_all()])) +' DA')))
        self.ui.filterpayment_combobox.addItems(['student', 'teacher', 'profit'])
        self.ui.filterpayment_combobox.setCurrentText('profit')
        self.ui.calendarWidget.currentPageChanged.connect(self.handle_ok_click)
        self.ui.calendarWidget.selectionChanged.connect(self.handle_ok_click)
        self.months = calendar.month_name[1:]
        self.ui.with_button.clicked.connect(self.handle_with_click)
        self.ui.show_all_classes_button.clicked.connect(lambda: (self.Classes.setFilter(None), self.Classes.select()))
        self.ui.show_all_students_button.clicked.connect(lambda: self.Students.setFilter(None))
        #connect form buttons
        self.TeachersAddForm.ui.add_button.clicked.connect(self.add_teacher)
        self.StudentsAddForm.ui.add_button.clicked.connect(self.add_student)
        self.ClassAddForm.ui.add_button.clicked.connect(self.add_class)
        self.TeachersEditForm.ui.save_button.clicked.connect(self.edit_teacher)
        self.StudentsEditForm.ui.save_button.clicked.connect(self.edit_student)
        self.ClassEditForm.ui.save_button.clicked.connect(self.edit_class)

        self.ClassFilter.dataChanged.connect(self.filter_class)


    def handle_with_click(self):
        self.ui.payment_tableview.clearSelection()
        self.ui.with_button.setEnabled(False)
        record = self.Payment.selectedRecord()
        if record['type'] == 'student':
            self.StudentCard.show(self.Students.get(record['with']))
        else: self.TeacherCard.show(self.Teachers.get(record['with']))

    def handle_ok_click(self, year = None, month = None):
        if self.ui.month_radioButton.isChecked():
            if not month:
                month = self.ui.calendarWidget.selectedDate().toString("MMMM")
            else: month = self.months[month-1]
            t = self.ui.filterpayment_combobox.currentText()
            if t == 'profit':
                self.Payment.setFilter(f"month = '{month}'")
            else: self.Payment.setFilter(f"month = '{month}' AND type = '{t}'")
            self.ui.profit_label.setText(str(sum([float(i['amount']) for i in self.Payment.get_all()])) +' DA')
        else:
            date = self.ui.calendarWidget.selectedDate().toString('yyyy-MM-dd')
            t = self.ui.filterpayment_combobox.currentText()
            if t == 'profit':
                self.Payment.setFilter(f"date = '{date}'")
            else: self.Payment.setFilter(f"date = '{date}' AND type = '{t}'")
            self.ui.profit_label.setText(str(sum([float(i['amount']) for i in self.Payment.get_all()])) +' DA')

            


    def show_info(self):
        layouts = [self.ui.elementry_layout, self.ui.middle_layout, self.ui.high_layout]
        [self.clear_layout(l) for l in layouts]
        for i, level in enumerate(['Elementry school', 'Middle school', 'High school']):
            for subject in self.Subjects.get_all():
                d = {'subject': subject['subject_name'], 'level': level}
                label = ClickableLabel(f"{subject['subject_name']}:\n{self.Teachers.number_of_records(d)} teachers")
                label.clicked.connect(lambda  s=subject['subject_name'], l=level : (self.ui.teacher_stackedwidget.setCurrentWidget(self.ui.teachers_list_widget), self.Teachers.setFilter(f"subject = '{s}' AND level = '{l}'"), self.Teachers.select()))
                layouts[i].addWidget(label)
        self.ui.teacher_stackedwidget.setCurrentWidget(self.ui.teachers_info_widget)



    def handle_selection_user_changed(self):
        if self.ui.users_tableView.selectionModel().currentIndex().row()==0:
            self.ui.edit_user_button.setEnabled(True)
            self.ui.delete_user_button.setEnabled(False)
            return
        self.ui.delete_user_button.setEnabled(True)
        self.ui.edit_user_button.setEnabled(True)


    def tab_clicked(self, i):
        self.Classes.setFilter('') 
        self.Teachers.setFilter('')
        self.Students.setFilter('')
        if i == 4:
            self.Payment.setFilter(f" month = '{datetime.datetime.now().strftime('%B')}'")
            self.ui.profit_label.setText(str(sum([float(i['amount']) for i in self.Payment.get_all()])) +' DA')   
        if i == 1:
            self.ui.teacher_stackedwidget.setCurrentWidget(self.ui.teachers_list_widget)

    ### implement the crud functions
    # add crud functions
    def  add_teacher(self):
        id = str(uuid.uuid4())
        self.Teachers.add(id, *self.TeachersAddForm.get_data().values())
        self.TeachersAddForm.close()
    def add_student(self):
        id = str(uuid.uuid4())
        self.Students.add(id, *self.StudentsAddForm.get_data().values())
        self.StudentsAddForm.close()
    def add_class(self):
        id = str(uuid.uuid4())
        self.Classes.add(id, *self.ClassAddForm.get_data().values())
        self.ClassAddForm.close()
    def add_subject(self):
        add_dialogue = QtWidgets.QInputDialog()
        text, ok = add_dialogue.getText(self.ui.subject_widget, 'new subject', 'Enter Subject name:')
        if ok: 
            self.Subjects.add(text)
            self.Subjects.add_button(text)
            self.Subjects.subject_buttons[-1].clicked.connect(lambda: (self.Classes.setFilter(f"subject = '{text}'"), self.ui.tabs.setCurrentWidget(self.ui.classes_tab)))
    def add_classroom(self):
        add_dialogue = QtWidgets.QInputDialog()
        text, ok = add_dialogue.getText(self.ui.classroom_widget, 'new classroom', 'Enter Classroom name:')
        if ok: 
            self.Classrooms.add(text)
            self.Classrooms.add_button(text)
            self.Classrooms.classroom_buttons[-1].clicked.connect(lambda: (self.Classes.setFilter(f"classroom = '{text}'"), self.ui.tabs.setCurrentWidget(self.ui.classes_tab)))
    # delete crud  functions 
    def delete_teacher(self):
        self.clear_selection(self.teacher_buttons, self.ui.teachers_table)
        self.Teachers.delete(self.Teachers.data(self.Teachers.index(self.ui.teachers_table.selectionModel().currentIndex().row(),0)))
        self.ui.delete_teacher_button.setEnabled(False)
        self.ui.edit_teacher_button.setEnabled(False)
        self.ui.open_teacher_button.setEnabled(False)
    def delete_student(self):
        self.clear_selection(self.student_buttons, self.ui.students_table)
        self.Students.delete(self.Students.data(self.Students.index(self.ui.students_table.selectionModel().currentIndex().row(),0)))
        self.ui.delete_student_button.setEnabled(False)
        self.ui.edit_student_button.setEnabled(False)
        self.ui.open_student_button.setEnabled(False)
    def delete_class(self):
        self.clear_selection(self.class_buttons, self.ui.classe_table)
        self.Classes.delete(self.Classes.data(self.Classes.index(self.ui.classe_table.selectionModel().currentIndex().row(),0)))
        self.ui.delete_class_button.setEnabled(False)
        self.ui.edit_class_button.setEnabled(False)
        self.ui.open_class_button.setEnabled(False)
    # edit crud functions
    def edit_teacher(self):
        self.clear_selection(self.teacher_buttons, self.ui.teachers_table)
        self.Teachers.update(self.TeachersEditForm.get_data())
        self.TeachersEditForm.close()
    def edit_student(self):
        self.clear_selection(self.student_buttons, self.ui.students_table)
        self.Students.update(self.StudentsEditForm.get_data())
        self.StudentsEditForm.close()
    def edit_class(self):
        self.clear_selection(self.class_buttons, self.ui.classe_table)
        self.Classes.update(self.ClassEditForm.get_data())
        self.ClassEditForm.close()

    def remove_filter(self):
        self.ClassFilter.delete(self.ClassFilter.selectedRecord()['column'])
        filter_query = ''
        for i, filter in enumerate(self.ClassFilter.get_all()):
            if i != 0:
                filter_query += ' AND '
            filter_query+= f"{filter['column']} = '{filter['value']}'" 
        self.Classes.setFilter(filter_query)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                layout.removeWidget(widget)
                widget.deleteLater()

    def clear_selection(self, buttons, tv):
        tv.clearSelection()
        for button in buttons:
            button.setEnabled(False)
    
    def filter_class(self):
        filter_query = ''
        for i, filter in enumerate(self.ClassFilter.get_all()):
            if i != 0:
                filter_query += ' AND '
            filter_query+= f"{filter['column']} = '{filter['value']}'" 
        self.Classes.setFilter(filter_query)     


if __name__ == "__main__":
    import sys
    initialize_db()
    app = QtWidgets.QApplication(sys.argv)
    login_window = LoginWindow()
    if login_window.exec_() == QtWidgets.QDialog.Accepted:
        MainWindow = MY_MainWindow(login_window.user)
        MainWindow.show()
        sys.exit(app.exec_())

