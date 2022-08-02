# pyuic6 MainWindow.ui -o MainWindow.py
import sys

from PyQt6 import QtWidgets

from MainWindow import Ui_MainWindow
from databases import SqliteDatabase
from viewer import Viewer


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()

db = SqliteDatabase("db.db")

table_widget: QtWidgets.QTableWidget = window.findChild(QtWidgets.QTableWidget, "tableView")
sql_widget: QtWidgets.QTextEdit = window.findChild(QtWidgets.QTextEdit, "sqlView")
errors_widget: QtWidgets.QLineEdit = window.findChild(QtWidgets.QLineEdit, "errorsView")
table_select_widget: QtWidgets.QComboBox = window.findChild(QtWidgets.QComboBox, "tableSelect")
filter_input_widget: QtWidgets.QLineEdit = window.findChild(QtWidgets.QLineEdit, "filterInput")

viewer = Viewer(db, table_widget, sql_widget, errors_widget, table_select_widget, filter_input_widget)

window.show()
app.exec()

