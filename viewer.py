from typing import List, Tuple, Callable

from PyQt6 import QtWidgets

import sql_helper
from databases import Database


class Viewer:
    def __init__(self,
                 database: Database,
                 table_widget: QtWidgets.QTableWidget,
                 sql_widget: QtWidgets.QTextEdit,
                 errors_widget: QtWidgets.QLineEdit,
                 table_select_widget: QtWidgets.QComboBox):
        """
        Initializes the viewer.\n
        :param database: The database object
        :param table_widget: The table widget
        :param sql_widget: The sql text widget
        :param errors_widget: The error text widget
        :param table_select_widget: The table select combo box widget
        """
        self._database: Database = database
        self._table_view: TableView = TableView(table_widget)
        self._sql_view: SqlView = SqlView(sql_widget, self.update_sql)
        self._errors_layout: ErrorsView = ErrorsView(errors_widget)
        self._table_select: TableSelect = TableSelect(table_select_widget, self.init_table)

        self._table_select.set_tables(database.get_tables())

    def init_table(self, table_name: str):
        """
        Initializes the table with 'SELECT * FROM <table_name>'.\n
        :param table_name: The table name
        """
        table = self._database[table_name]
        columns = table.get_columns()
        sql = table.select("*").resolve()
        data = self._database.fetch(sql, ())

        self._table_view.set_columns(columns)
        self._table_view.set_data(data)
        self._sql_view.set_text(sql)

    def update_sql(self, sql: str):
        """
        Updates the table for a given sql command.\n
        :param sql: The sql command
        """
        try:
            data = self._database.fetch(sql, ())
            selected_columns = sql_helper.get_selected_columns(sql)
            self._table_view.set_columns(selected_columns)
            self._table_view.set_data(data)
            self._errors_layout.clear()
        except Exception as error:
            self._errors_layout.set(str(error))


class ErrorsView:
    def __init__(self, widget: QtWidgets.QLineEdit):
        """
        Initializes the error view.\n
        :param widget: The line edit widget
        """
        self._widget: QtWidgets.QLineEdit = widget
        self._widget.setStyleSheet("color: red")

    def set(self, error: str):
        """
        Sets the error text.\n
        :param error: The error text
        """
        self._widget.setText(f"{error}")

    def clear(self):
        """
        Clears the error text.\n
        """
        self._widget.setText("")


class TableView:
    def __init__(self, widget: QtWidgets.QTableWidget):
        """
        Initializes the table view.\n
        :param widget: The table widget
        """
        self._widget: QtWidgets.QTableWidget = widget

    def set_columns(self, columns: List[str]):
        """
        Sets the columns.\n
        :param columns: The column names
        """
        self._widget.setColumnCount(len(columns))
        self._widget.setHorizontalHeaderLabels(columns)

    def set_data(self, data: List[Tuple]):
        """
        Sets the table data.\n
        :param data: The data
        """
        self.clear()
        for entry in data:
            row_position = self._widget.rowCount()
            self.insert_row(row_position, entry)

    def clear(self):
        """
        Removes all rows.\n
        """
        for i in range(0, self._widget.rowCount()):
            self._widget.removeRow(0)

    def insert_row(self, row: int, entry: Tuple):
        """
        Inserts a row at a given index.\n
        :param row: The row index
        :param entry: The row
        """
        if row > self._widget.rowCount():
            raise IndexError("Row index out of bounce.")
        self._widget.insertRow(row)
        for i in range(len(entry)):
            self._widget.setItem(row, i, QtWidgets.QTableWidgetItem(str(entry[i])))

    def append_row(self, entry: Tuple):
        """
        Appends a row to the table.\n
        :param entry: The row
        """
        index = self._widget.rowCount()
        self.insert_row(index, entry)

    def remove_row(self, row: int):
        """
        Removes a row from a given index.\n
        :param row: The index
        """
        if row > self._widget.rowCount():
            raise IndexError("Row index out of bounce.")
        self._widget.removeRow(row)


class SqlView:
    def __init__(self, widget: QtWidgets.QTextEdit, update_fn: Callable[[str], None]):
        """
        Initializes the sql view.\n
        :param widget: The text edit widget
        :param update_fn: The function that is called, when the content of the text edit changes
        """
        self._widget: QtWidgets.QTextEdit = widget
        self._widget.textChanged.connect(self._on_text_changed)
        self._update_fn: Callable[[str], None] = update_fn

    def set_text(self, text: str):
        """
        Set the text of the text edit
        :param text: The text
        """
        self._widget.setPlainText(text)

    def _on_text_changed(self):
        text = self._widget.toPlainText()
        self._update_fn(text)


class TableSelect:
    def __init__(self, widget: QtWidgets.QComboBox, select_fn: Callable[[str], None]):
        """
        Initializes the table select.\n
        :param widget: The table select combo box widget
        :param select_fn: The select function
        """
        self._widget: QtWidgets.QComboBox = widget
        self._select_fn: Callable[[str], None] = select_fn
        self._widget.currentIndexChanged.connect(self._on_select)

    def _on_select(self):
        table = self._widget.currentText()
        self._select_fn(table)

    def set_tables(self, tables: List[str]):
        """
        Sets the items of the select.\n
        :param tables: The table names
        """
        self.clear()
        self._widget.addItems(tables)

    def clear(self):
        """
        Clears the select.\n
        """
        for i in range(0, self._widget.count()):
            self._widget.removeItem(0)