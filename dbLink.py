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
    
    def addExpense(self, expense, price, date):
        
        if expense in self.data.keys():
            old_price = self.data[expense]["Price"]
            self.data[expense] = {"Price": price + old_price, "Date": date}
        else:
            self.data[expense] = {"Price": price , "Date": date}

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

