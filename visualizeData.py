import matplotlib.pyplot as plt
from CreateExpenseWindow import ExpenseApp


def visualize_expenses(self, year, month):
    # Get the expenses for the specified year and month
    expenses = self.data.getExpensesByMonth(year, month)
    
    if not expenses:
        self.show_error_message(f"No expenses found for {month}/{year}.")
        return

    # Prepare data for visualization
    expense_names = list(expenses.keys())
    expense_values = list(expenses.values())

    # Create a pie chart
    plt.figure(figsize=(10, 6))
    plt.pie(expense_values, labels=expense_names, autopct='%1.1f%%', startangle=140)
    plt.title(f'Expenses for {month}/{year}')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.show()

    # Create a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(expense_names, expense_values, color='skyblue')
    plt.xlabel('Expense')
    plt.ylabel('Amount')
    plt.title(f'Expenses for {month}/{year}')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
