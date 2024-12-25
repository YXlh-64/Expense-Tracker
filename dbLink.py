from PyQt5.QtSql import QSqlDatabase, QSqlQuery

class ExpenseDB:
    def __init__(self):
        #initially no DB connection
        self.connection = None
        
        #QSalDatabase.defaultConnection is the default connection name
        driver = "QSQLITE" #a required argument specifying the supported sql driver used to connect to the DB
        self.connection = QSqlDatabase.addDatabase(driver)
        
        #setting a DB name
        self.connection.setDatabaseName("expense_tracker.sqlite")
        print(self.connection)
        #if the connection cannot be established
        if not self.connection.open():
            print("Connection to the database failed")
            sys.exit(1) 
            
        #create the expenses table if it does not exist
        self.createTable()
        

    
    def createTable(self):
        query = QSqlQuery()
        #in case the user deletes an expense it will not be displayed (archived is true)
        create_table_query = """
            CREATE TABLE IF NOT EXISTS expenses(
                expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_name TEXT NOT NULL,
                expense_category TEXT NOT NULL,
                expense_price FLOAT NOT NULL,
                expense_date DATE NOT NULL,
                expense_archived BOOLEAN NOT NULL
            )
        """
        if not query.exec(create_table_query):
            print(f"Failed to create table: {query.lastError().text()}")
            
    def displayExpenses(self):
        query = QSqlQuery()
        query.prepare("SELECT * FROM expenses WHERE expense_archived = ?")
        query.addBindValue(False)
        if not query.exec():
            print(f"display expenses")
        
        rows = []
        while query.next():
            row = []
            for i in range(4):
                row.append(query.value(i+1))
            rows.append(row)
        print(rows)

        return rows
            
    def countExpenses(self):
        query = QSqlQuery()
        query.prepare("SELECT COUNT(*) FROM expenses WHERE expense_archived = ?")
        query.addBindValue(False)
        
        if not query.exec():
            print(f"Failed to count expenses: {query.lastError().text()}")
            return 0 

        if query.next():
            return query.value(0) 
        return 0  # Return 0 if no results

    def addExpense(self, expense, category, price, date):
        
        query = QSqlQuery()
        query.prepare("INSERT INTO expenses (expense_name, expense_category, expense_price, expense_date, expense_archived) VALUES (?, ?, ?, ?, ?)")
        query.addBindValue(expense)
        query.addBindValue(category)
        query.addBindValue(price)
        query.addBindValue(date)
        query.addBindValue(False)
        if not query.exec():
            print(f"Failed to add expense: {query.lastError().text()}")
            
        self.consolidateExpenses()

    def deleteExpense(self, expense, date):
        query = QSqlQuery()
        query.prepare("UPDATE expenses SET expense_archived = ? WHERE expense_name = ? AND expense_date = ?")
        query.addBindValue(True)
        query.addBindValue(expense)
        query.addBindValue(date)
        if not query.exec():
            print(f"Failed to delete expense: {query.lastError().text()}")
            
        self.consolidateExpenses()

    

    # a function which checks whether there are two or more occurrences of expenses in the same date and expense name
    def consolidateExpenses(self):
        # Step 1: Retrieve grouped expenses
        query = QSqlQuery()
        query.prepare("""
            SELECT expense_name, expense_category, expense_date, SUM(expense_price) AS total_price
            FROM expenses
            WHERE expense_archived = ?
            GROUP BY expense_name, expense_category, expense_date
            HAVING COUNT(*) > 1
        """)
        query.addBindValue(False)
        
        if not query.exec():
            print(f"Failed to retrieve grouped expenses: {query.lastError().text()}")
            return
        
        grouped_expenses = []
        while query.next():
            expense_name = query.value(0)
            expense_category = query.value(1)
            expense_date = query.value(2)
            total_price = query.value(3)
            grouped_expenses.append((expense_name, expense_category, expense_date, total_price))
        
        # Step 2: Remove duplicate expenses and insert the consolidated row
        for expense_name, expense_category, expense_date, total_price in grouped_expenses:
            # Delete the original rows
            delete_query = QSqlQuery()
            delete_query.prepare("""
                DELETE FROM expenses
                WHERE expense_name = ? AND expense_category = ? AND expense_date = ? AND expense_archived = ?
            """)
            delete_query.addBindValue(expense_name)
            delete_query.addBindValue(expense_category)
            delete_query.addBindValue(expense_date)
            delete_query.addBindValue(False)
            
            if not delete_query.exec():
                print(f"Failed to delete duplicate expenses: {delete_query.lastError().text()}")
                continue
            
            # Insert the consolidated row
            insert_query = QSqlQuery()
            insert_query.prepare("""
                INSERT INTO expenses (expense_name, expense_category, expense_price, expense_date, expense_archived)
                VALUES (?, ?, ?, ?, ?)
            """)
            insert_query.addBindValue(expense_name)
            insert_query.addBindValue(expense_category)
            insert_query.addBindValue(total_price)
            insert_query.addBindValue(expense_date)
            insert_query.addBindValue(False)
            
            if not insert_query.exec():
                print(f"Failed to insert consolidated expense: {insert_query.lastError().text()}")
