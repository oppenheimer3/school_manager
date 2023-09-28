from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery


def initialize_db():
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('database.db')
    if not db.open():
        print("Failed to open the database.")


class TableModel(QSqlTableModel):
    name = str
    fields = dict
    childs = None
    def __init__(self, table_view = None):
        super().__init__()
        if table_view:
            self.table_view = table_view
            self.table_view.setModel(self)
            header = self.table_view.horizontalHeader()
            header.setDefaultSectionSize(270)

        self.query = QSqlQuery()
        create_query = f"CREATE TABLE IF NOT EXISTS {self.name} ("
        field_strings = [f"{field} {data_type}" for field, data_type in self.fields.items()]
        create_query += ", ".join(field_strings)
        create_query += ")"
        self.query.exec(create_query)
        self.setTable(self.name)
        self.select()
        self.setEditStrategy(QSqlTableModel.OnFieldChange)



    def add(self, *args):
        self.query.prepare(f"INSERT INTO {self.name} ("+", ".join(self.fields.keys())+") VALUES ("+ ", ".join(['?'] * len(self.fields.keys()))+")")  # Replace with your table name and column names
        for arg in args:
            self.query.addBindValue(arg)
        if not self.query.exec():
            print('failed to add')
        self.select()

    
    def delete(self, pk):
        delete_query = f"DELETE FROM {self.name} WHERE {list(self.fields.keys())[0]} = :pk"
        self.query.prepare(delete_query)
        self.query.bindValue(":pk", pk)
        self.query.exec()
        self.select()
        if self.childs:
            for table, pkey in self.childs.items():
                delete_query = f"DELETE FROM {table} WHERE {pkey} = :pk"
                self.query.prepare(delete_query)
                self.query.bindValue(":pk", pk)
                self.query.exec()            
                

    def delete_all(self):
        self.query.exec_(f"DELETE FROM {self.name}")
        self.select()

    
    def get(self, pk):
        self.setFilter(f"{list(self.fields.keys())[0]}='{pk}'")
        self.select()
        record = {i:self.record(0).value(i) for i in self.fields.keys()}
        self.setFilter('')
        return record
    
    def selectedRecord(self, tv=None):
        if not tv :
            return {col:self.record(self.table_view.selectionModel().currentIndex().row()).value(col) for col in self.fields.keys()}
        else:               
            return {col:self.record(tv.selectionModel().currentIndex().row()).value(col) for col in self.fields.keys()}
         
    def get_all(self):
        return [{i:self.record(j).value(i) for i in self.fields.keys()} for j in range(self.rowCount())]
    
    def update(self, data, pk=None):
        if pk is None:
            pk = self.table_view.selectionModel().currentIndex().row()
        for key,  value in data.items():
            self.setData(self.index(pk, self.fieldIndex(key)), value)
        self.submitAll()

    def update_by_pk(self, pk, data):
        query = f"UPDATE {self.name}"
        for i, (key, value) in enumerate(data.items()):
            if i ==0:
                query += f" SET {key} = '{value}' "
                continue
            query += f", {key} = '{value}' "
        query += f"WHERE {next(iter(self.fields))} = '{pk}';"
        if not self.query.exec(query):
            print('failed to excute')

        
    
    def search(self,cols, search_str):
        filter_expression = ''
        for col in cols:
            if filter_expression:
                filter_expression += f"OR {col} LIKE '%{search_str}%'" 
            else: filter_expression += f"{col} LIKE '%{search_str}%'"
        self.setFilter(filter_expression)
        self.select()
        return self.get_all()
    
    def hide_columns(self, cols, tv = None):
        if tv:
            for col in cols:
                tv.setColumnHidden(col, True)    
        else:        
            for col in cols:
                self.table_view.setColumnHidden(col, True)
    
    def number_of_records(self, d):
        query_str = ''
        for i, (key, val) in enumerate(d.items()):
            if i != 0:
                query_str += " AND "
                query_str +=f"{key} = '{val}'"
            else:
                query_str +=f"{key} = '{val}'"
        self.setFilter(query_str)
        self.select()
        return self.rowCount()



        


### My Models

class Teachers(TableModel):
    name = "Teachers"
    fields = {
        "id": "TEXT PRIMARY KEY",
        "first_name": "TEXT",
        "last_name": "TEXT",
        "phone": "TEXT",
        "email": "TEXT",
        "subject": "TEXT",
        "level": "TEXT"
        }

class Students(TableModel):
    name = "Students"
    fields = {
        "id": "TEXT PRIMARY KEY",
        "first_name": "TEXT",
        "last_name": "TEXT",
        "phone": "TEXT",
        "email": "TEXT",
        "photo": "BLOB"
    }
    childs ={
        "ClassStudents":"student_id"
    }
class Classes(TableModel):
    name = "Classes"
    fields  = {
        "id" : "TEXT PRIMARY KEY",
        "level": "TEXT",
        "year":"TEXT",
        "subject": "TEXT",
        "teacher": "TEXT",
        "classroom": "TEXT",
        "day": "TEXT",
        "start_time": "TEXT",
        "end_time": "TEXT",
        "teacher_id": "TEXT",
        "price":"TEXT",
        "session_price":"TEXT",
        "teacher_payement":"TEXT",
        "salary":"TEXT"
    }
    childs ={
        "ClassStudents":"class_id"
    }

class ClassStudents(TableModel):
    name = "ClassStudents"
    fields = {
        "id":"TEXT PRIMARY KEY",
        "name": "TEXT",
        "level": "TEXT",
        "year": "TEXT",
        "subject":"TEXT",
        "teacher":"TEXT", 
        "student_id": "TEXT", 
        "class_id": "TEXT"
    }
class Subjects(TableModel):
    name = "Subjects"
    fields = {
        "subject_name": "TEXT",
    }


class Classrooms (TableModel):
    name = "Classrooms"
    fields = {
        "classroom_name": "TEXT"
    }


class ClassRecords(TableModel):
    name = "ClassRecords"
    fields = {
        "id": "TEXT PRIMARY KEY", 
        "class_id": "integer", 
        "class_date": "TEXT"
    }
class Attendance(TableModel):
    name = "Attendance"
    fields = {
        "id": "TEXT PRIMARY KEY",
        "student_name": "TEXT", 
        "time": "TEXT",
        "student_id": "TEXT",
        "class_record_id": "TEXT"

    }
class RegistrationTable(TableModel):
    name = "RegistrationTable"
    fields = {
        "id": "TEXT PRIMARY KEY", 
        "name": "TEXT",
        "status": "TEXT"
    }
class ClassFilter(TableModel):
    name = "ClassFilter"
    fields = {
        "column": "TEXT PRIMARY KEY", 
        "value": "TEXT"
    }

class TimeManagement(TableModel):
    name = "TimeManagement"
    fields = {
        "Time": "TEXT PRIMARY KEY", "Monday": "TEXT", "Tuesday": "TEXT", "Wednesday": "TEXT", "Thursday": "TEXT", "Friday": "TEXT", "Saturday": "TEXT", "Sunday": "TEXT"
}

class ClassPayement(TableModel):
    name = "ClassPayement"
    fields = {
        "id":"TEXT PRIMARY KEY", 
        "class_student_id": "TEXT",
        "month":"TEXT",
        "year":"TEXT",
        "date": "TEXT",
        "status":"TEXT",
        "month_payement":"TEXT"
    }

class TeacherPayement(TableModel):
    name = "TeacherPayement"
    fields = {
        "class_id":"TEXT PRIMARY KEY", 
        "number_of_students":"TEXT",
        "paid_students":"TEXT",
        "class_salary":"TEXT"
    }

class Users(TableModel):
    name = "Users"
    fields = {
        "username": "TEXT PRIMARY KEY",
        "password": "TEXT",
        "role": "TEXT"
    }

class Payment(TableModel):
    name = "Payment"
    fields = {
        "id": "TEXT PRIMARY KEY",
        "date": "TEXT",
        "with": "TEXT",
        "amount": "TEXT",
        "type": "TEXT",
        "month": "TEXT"
    }