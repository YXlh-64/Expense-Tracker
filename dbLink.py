import json

class ManipulateDB:
    def __init__(self):
        try:
            with open("data.json", 'r') as db:
                self.data = json.load(db)
        
        #in case the file does not exist
        except FileNotFoundError:
            #notifying the user
            print("file not found")

            self.data = {}

            with open("data.json", 'r') as db:
                db.write("{}")
    
    def addExpense(self, expense, price):
        
        if expense in self.data.keys():
            self.data[expense] += price
        else:
            self.data[expense] = price

        self.writeToDB()

    def deleteExpense(self, expense):
        if expense in self.data.keys():
            del self.data[expense]
        else:
            pass
        
        self.writeToDB()
    
    def writeToDB(self):
        with open("data.json", "w") as db:
            json.dump(self.data, db, indent = 4)

"""     def editExpense(self, expense, newPrice):
        if expense in self.data.keys:
            self.data[expense] = newPrice """

""" test = ManipulateDB()

test.addExpense(expense="miaw", price=23)
test.deleteExpense("Veg") """

