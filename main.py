import sys
from PyQt5.QtWidgets import (
    QApplication)
from CreateExpenseWindow import ExpenseApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExpenseApp()
    window.show()
    sys.exit(app.exec_())
