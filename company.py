class Company:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.licenses = []
    
    def add_license(self, License):
        self.licenses.append(License)
        
    def __str__(self):
        return f"Company: {self.name}, Email: {self.email}, License: {self.licenses}"
    
class License:
    def __init__(self, license_name, expiry_date, quantity):
        self.name = license_name
        self.expiry_date = expiry_date
        self.quantity = quantity
    def __str__(self):
        return f"License: {self.name}, Expiry Date: {self.expiry_date}, Quantity: {self.quantity}"
