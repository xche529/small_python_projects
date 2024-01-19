class Company:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.license = []
    
    def add_license(self, License):
        self.license.append(License)
        
class License:
    def __init__(self, license, expiry_date, quantity):
        self.name = license
        self.expiry_date = expiry_date
        self.quantity = quantity
