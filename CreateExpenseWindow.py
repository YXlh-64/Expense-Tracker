from fpdf import FPDF
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QLineEdit, QLabel, QPushButton, QComboBox, QMenuBar, QMenu, QMessageBox
)
from PyQt5.QtCore import Qt

from dbLink import ExpenseDB
from datetime import datetime

#visualization
import matplotlib.pyplot as plt
from io import BytesIO
from PyQt5.QtGui import QPixmap
from collections import defaultdict

class ExpenseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set up the main window
        self.setWindowTitle("Expense Tracker")
        self.setGeometry(100, 100, 600, 300)

        # Create a central widget and set it as the central widget of the QMainWindow
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a vertical layout for the central widget
        layout = QVBoxLayout(central_widget)
        self.layout=layout

        
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

        # Create labels and text fields for "Expense", "Category", "Price", and "Date"
        expense_label = QLabel("Expense:")
        self.expense_input = QLineEdit()
        self.expense_input.setFixedWidth(150)
        
        category_label = QLabel("Category:")
        self.category_input = QLineEdit()
        self.category_input.setFixedWidth(150)
        
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
        top_panel.addWidget(category_label)
        top_panel.addWidget(self.category_input)
        top_panel.addWidget(price_label)
        top_panel.addWidget(self.price_input)
        top_panel.addWidget(date_label)
        top_panel.addWidget(self.date_input)
        
        top_panel.addWidget(add_button)


        # Create the filter panel
        filter_panel = QHBoxLayout()
        layout.addLayout(filter_panel)

        self.filter_category = QLineEdit()
        self.filter_category.setPlaceholderText("Filter by Category")
        self.filter_category.textChanged.connect(self.apply_filters)

        self.filter_month = QLineEdit()
        self.filter_month.setPlaceholderText("Filter by Month (MM)")
        self.filter_month.textChanged.connect(self.apply_filters)

        self.filter_sort = QComboBox()
        self.filter_sort.addItem("Sort By")
        self.filter_sort.addItems(["Alphabetical", "Price (Low to High)", "Price (High to Low)"])
        self.filter_sort.currentIndexChanged.connect(self.apply_filters)

        filter_panel.addWidget(QLabel("Filters:"))
        filter_panel.addWidget(self.filter_category)
        filter_panel.addWidget(self.filter_month)
        filter_panel.addWidget(self.filter_sort)
        

        # Create the table to display expenses
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # Extra columns for the delete and category
        self.table.setHorizontalHeaderLabels(["Expense", "Category", "Price", "Date", "Actions"])
        layout.addWidget(self.table)

        # Create the bottom panel for displaying the total
        total_label = QLabel("Total:")
        self.total_value = QLabel("0.00")
        total_layout = QHBoxLayout()
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_value)
        layout.addLayout(total_layout)

        # Initialize with data from DB
        self.DB = ExpenseDB()
        self.all_expenses = self.DB.displayExpenses()  
        self.display_expenses(self.all_expenses)  # Display all expenses initially
        
        self.table.setRowCount(self.DB.countExpenses())
        rows = self.DB.displayExpenses()
        for i in range (len(rows)):
            for j in range (4):
                self.table.setItem(i, j, QTableWidgetItem(str(rows[i][j])))
                
            self.add_delete_button(i)
                
        
        self.update_total()

       # Add the button to navigate to the report page
        report_button = QPushButton("Generate Reports")
        report_button.clicked.connect(self.open_report_page)
        layout.addWidget(report_button)


    def add_expense(self):
        # Get the values from the input fields
        expense = self.expense_input.text().strip()
        category = self.category_input.text().strip()
        price_text = self.price_input.text().strip()
        date = self.date_input.text().strip()

        # Validate inputs
        if not expense or expense.isdigit():
            self.show_error_message("Expense name must be a non-numeric text.")
            return

        if not category or category.isdigit():
            self.show_error_message("Category name must be a non-numeric text.")
            return

        try:
            price = float(price_text)
        except ValueError:
            self.show_error_message("Price must be a valid number.")
            return

        if not self.validate_date_format(date):
            self.show_error_message("Date must be in the format YYYY-MM-DD.")
            return

        # Add to the database
        self.DB.addExpense(expense, category, price, date)

        # Add a new row to the table
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(expense))
        self.table.setItem(row_position, 1, QTableWidgetItem(category))
        self.table.setItem(row_position, 2, QTableWidgetItem(str(price)))
        self.table.setItem(row_position, 3, QTableWidgetItem(date))

        # Add a delete button to the row
        self.add_delete_button(row_position)

        # Clear the input fields
        self.expense_input.clear()
        self.category_input.clear()
        self.price_input.clear()
        self.date_input.clear()

        # Update the total
        self.update_total()

        

    def display_expenses(self, expenses):
        """Display expenses in the table."""
        self.table.setRowCount(len(expenses))
        for i, row in enumerate(expenses):
            for j in range(4):
                self.table.setItem(i, j, QTableWidgetItem(str(row[j])))
            self.add_delete_button(i)
        self.update_total()

    def add_delete_button(self, row):
        # Create a delete button for the given row
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_expense)
        self.table.setCellWidget(row, 4, delete_button)

    def delete_expense(self):
        # Find the row of the delete button that was clicked
        button = self.sender()
        if button:
            # Get the row position of the clicked delete button
            index = self.table.indexAt(button.pos())
            if index.isValid():
                # Get the expense name from the first column of the row
                expense_name = self.table.item(index.row(), 0).text()
                expense_date = self.table.item(index.row(), 3).text()

                # Delete from database
                self.DB.deleteExpense(expense_name, expense_date)

                # Remove the row from the table
                self.table.removeRow(index.row())
                
                # Update the total
                self.update_total()

    def update_total(self):
        # Calculate the total price
        total = 0.0
        for row in range(self.table.rowCount()):
            price_item = self.table.item(row, 2)
            if price_item:
                try:
                    total += float(price_item.text())
                except ValueError:
                    print("cannot convert to a number>>>")
        self.total_value.setText(f"{total:.2f}")


    def apply_filters(self):
        """Apply filters to the displayed expenses."""
        filtered_expenses = self.all_expenses

        # Filter by category
        category = self.filter_category.text().strip().lower()
        if category:
            filtered_expenses = [e for e in filtered_expenses if category in e[1].lower()]

        month = self.filter_month.text().strip()
        if month.isdigit() and 1 <= int(month) <= 12:
            formatted_month = f"{int(month):02d}"  # Ensure the month is in "MM" format
            filtered_expenses = [e for e in filtered_expenses if e[3][5:7] == formatted_month or e[3][5:6] == formatted_month ]

        # Sort expenses
        sort_index = self.filter_sort.currentIndex()
        if sort_index == 1:  # Alphabetical
            filtered_expenses.sort(key=lambda x: x[0].lower())
        elif sort_index == 2:  # Price (Low to High)
            filtered_expenses.sort(key=lambda x: float(x[2]))
        elif sort_index == 3:  # Price (High to Low)
            filtered_expenses.sort(key=lambda x: float(x[2]), reverse=True)

        self.display_expenses(filtered_expenses)

    def show_error_message(self, message):
        # Display an error message dialog
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Warning)
        error_dialog.setWindowTitle("Input Error")
        error_dialog.setText(message)
        error_dialog.exec_()



    def validate_date_format(self,date_str):
        """Validate the date format as YYYY-MM-DD."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    # this creates another page for the reports
    def open_report_page(self):
        """Open the report page."""
        # Create the report page
        self.report_page = QWidget(self)
        self.setCentralWidget(self.report_page)

        # Layout for the report page
        layout = QVBoxLayout(self.report_page)

        # Add buttons for generating written and visual reports
        written_report_button = QPushButton("Generate Written Report")
        written_report_button.clicked.connect(self.generate_written_report)

        visualize_report_button = QPushButton("Visualize Report")
        visualize_report_button.clicked.connect(self.visualize_report)

        back_button = QPushButton("Back to Expense Tracker")
        back_button.clicked.connect(self.back_to_main_page)

        layout.addWidget(written_report_button)
        layout.addWidget(visualize_report_button)
        layout.addWidget(back_button)

        # Placeholder label for displaying reports
        self.report_label = QLabel("Your report will appear here.")
        self.report_label.setWordWrap(True)
        layout.addWidget(self.report_label)

        # Placeholder for chart visualization
        self.chart_placeholder = QLabel("Your chart will appear here.")
        layout.addWidget(self.chart_placeholder)

        export_button = QPushButton("Export Written Report as PDF")
        export_button.clicked.connect(self.export_report_as_pdf)
        layout.addWidget(export_button)

        export_chart_button = QPushButton("Export Chart as Image")
        export_chart_button.clicked.connect(self.export_chart_as_image)
        layout.addWidget(export_chart_button)



    def back_to_main_page(self):
        """Go back to the main expense tracker page."""
        self.setCentralWidget(self.central_widget)

    def generate_written_report(self):
            
        """Generate a written summary report of expenses."""
        from collections import defaultdict

        # Summarize data
        category_totals = defaultdict(float)
        total_expense = 0.0
        for expense in self.all_expenses:
            category_totals[expense[1]] += float(expense[2])
            total_expense += float(expense[2])

        highest_category = max(category_totals.items(), key=lambda x: x[1])

        # Generate report text
        report_text = (
            f"Expense Report:\n\n"
            f"Total Expenses: {total_expense:.2f}\n"
            f"Highest Spending Category: {highest_category[0]} ({highest_category[1]:.2f})\n"
            f"Number of Transactions: {len(self.all_expenses)}\n\n"
            f"Category Breakdown:\n"
        )

        for category, total in category_totals.items():
            report_text += f" - {category}: {total:.2f}\n"

        # Display the report
        self.report_label.setText(report_text)


    def visualize_report(self):
        """Visualize the expense report as a pie chart."""


        # Summarize data
        category_totals = defaultdict(float)
        for expense in self.all_expenses:
            category_totals[expense[1]] += float(expense[2])

        # Create pie chart
        labels = list(category_totals.keys())
        sizes = list(category_totals.values())

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Save the chart as an image
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData(buf.read())

        # Display the chart
        self.chart_placeholder.setPixmap(pixmap)
        buf.close()
        return fig

    def export_chart_as_image(self):

        fig= self.visualize_report()
        # Save the current pie chart
        fig.savefig("Expense_Report_Chart.png")
        self.show_message("Chart exported as an image successfully!")

    def export_report_as_pdf(self):
        """Export the written report as a PDF."""

        # Get the report text
        report_text = self.report_label.text()

        # Create a PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add report text to PDF
        for line in report_text.split("\n"):
            pdf.cell(0, 10, line, ln=True)

        # Save the PDF
        pdf_file = "Expense_Report.pdf"
        pdf.output(pdf_file)
        self.show_message("Report exported as PDF successfully!")

    def show_message(self, message, title="Information"):
        """Show a message to the user."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()
