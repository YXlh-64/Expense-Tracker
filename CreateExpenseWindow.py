from dbLink import ManipulateDB
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QLineEdit, QLabel, QPushButton, QMenuBar, QMenu, QMessageBox
)
from PyQt5.QtCore import Qt

class ExpenseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data = ManipulateDB()
        
        # Set up the main window
        self.setWindowTitle("Expense Tracker")
        self.setGeometry(100, 100, 600, 300)

        # Create a central widget and set it as the central widget of the QMainWindow
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a vertical layout for the central widget
        layout = QVBoxLayout(central_widget)

        # Create a menu bar
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        
        file_menu = QMenu("File", self)
        edit_menu = QMenu("Edit", self)
        help_menu = QMenu("Help", self)
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(edit_menu)
        menu_bar.addMenu(help_menu)

        # Create the top panel for input fields and add button
        top_panel = QHBoxLayout()
        layout.addLayout(top_panel)

        # Create labels and text fields for "Expense" and "Price"
        expense_label = QLabel("Expense:")
        self.expense_input = QLineEdit()
        self.expense_input.setFixedWidth(150)

        price_label = QLabel("Price:")
        self.price_input = QLineEdit()
        self.price_input.setFixedWidth(100)

        date_label = QLabel("Date:")
        self.date_input = QLineEdit()
        self.date_input.setFixedWidth(100)
        
        # Create the button to add expenses
        add_button = QPushButton("Add Expense")
        add_button.clicked.connect(self.add_expense)
        
        # Add widgets to the top panel
        top_panel.addWidget(expense_label)
        top_panel.addWidget(self.expense_input)
        top_panel.addWidget(price_label)
        top_panel.addWidget(self.price_input)
        top_panel.addWidget(date_label)
        top_panel.addWidget(self.date_input)
        
        top_panel.addWidget(add_button)

        # Create the table to display expenses
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # Extra column for the delete button
        self.table.setHorizontalHeaderLabels(["Expense", "Price", "Date", "Actions"])
        layout.addWidget(self.table)

        # Create the bottom panel for displaying the total
        total_label = QLabel("Total:")
        self.total_value = QLabel("0.00")
        total_layout = QHBoxLayout()
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_value)
        layout.addLayout(total_layout)

        # Initialize with data from DB
        initial_data = [(exp, desc["Price"], desc["Date"]) for exp, desc in self.data.data.items()]
        self.table.setRowCount(len(initial_data))
        for row, (expense, price, date) in enumerate(initial_data):
            self.table.setItem(row, 0, QTableWidgetItem(expense))
            self.table.setItem(row, 1, QTableWidgetItem(str(price)))
            self.table.setItem(row, 2, QTableWidgetItem(date))
            self.add_delete_button(row)
        
        self.update_total()

    def add_expense(self):
        # Get the values from the input fields
        expense_name = self.expense_input.text().strip()
        price_text = self.price_input.text().strip()
        date = self.date_input.text().strip()

        # Validate inputs
        if not expense_name or expense_name.isdigit():
            self.show_error_message("Expense name must be a non-numeric text.")
            return

        try:
            price = float(price_text)
        except ValueError:
            self.show_error_message("Price must be a valid number.")
            return

        # Add to the database
        self.data.addExpense(expense_name, price, date)

        # Add a new row to the table
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(expense_name))
        self.table.setItem(row_position, 1, QTableWidgetItem(str(price)))
        self.table.setItem(row_position, 2, QTableWidgetItem(date))
        
        # Add a delete button to the row
        self.add_delete_button(row_position)

        # Clear the input fields
        self.expense_input.clear()
        self.price_input.clear()
        self.date_input.clear()

        # Update the total
        self.update_total()

    def add_delete_button(self, row):
        # Create a delete button for the given row
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_expense)
        self.table.setCellWidget(row, 3, delete_button)

    def delete_expense(self):
        # Find the row of the delete button that was clicked
        button = self.sender()
        if button:
            # Get the row position of the clicked delete button
            index = self.table.indexAt(button.pos())
            if index.isValid():
                # Get the expense name from the first column of the row
                expense_name = self.table.item(index.row(), 0).text()

                # Delete from database
                self.data.deleteExpense(expense_name)

                # Remove the row from the table
                self.table.removeRow(index.row())
                
                # Update the total
                self.update_total()

    def update_total(self):
        # Calculate the total price
        total = 0.0
        for row in range(self.table.rowCount()):
            price_item = self.table.item(row, 1)
            if price_item:
                try:
                    total += float(price_item.text())
                except ValueError:
                    pass
        self.total_value.setText(f"{total:.2f}")

    def show_error_message(self, message):
        # Display an error message dialog
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Warning)
        error_dialog.setWindowTitle("Input Error")
        error_dialog.setText(message)
        error_dialog.exec_()
