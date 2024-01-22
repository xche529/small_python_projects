    

from tkinter import filedialog
import tkinter

class EmailWriter:
    def __init__(self, template_file_path):
        self.email_content = None
        self.license_content = None
        self.temp_license_content = None
        self.template_file_path = template_file_path
        self.get_template_content()
           
    def get_template_content(self):
        with open(self.template_file_path, 'r') as file:
            content = file.read()
            content_list = content.split("#")
            if len(content_list) != 2:
                print("模板文件格式错误")
                return
            self.email_content = content_list[0].strip()
            self.license_content = content_list[1].strip()

    def insert_email_content(self,company):
        licenses_str = ""
        max_license_name_length = 0
        for license in company.licenses:
            if len(license.name) > max_license_name_length:
                max_license_name_length = len(license.name)
        max_license_name_length += 10
        for license in company.licenses:
            print(license.name)
            licenses_str += self.create_license_string(license, max_license_name_length)
            licenses_str += "\n"
        self.email_content = self.email_content.replace("{{company_name}}", company.name)
        self.email_content = self.email_content.replace("{{license_info}}", licenses_str)

    def create_license_string(self, license, max_license_name_length):
        content_list = self.license_content.split("|")

        template = "{:<" + str(max_license_name_length) +"}" + "{:<15}" + "{} " * (len(content_list) - 2)


        for i in range(len(content_list)):
            if "{{license_name}}" in content_list[i]:
                content_list[i] = content_list[i].replace("{{license_name}}", str(license.name))
            if "{{license_quantity}}" in content_list[i]:
                content_list[i] = content_list[i].replace("{{license_quantity}}", str(license.quantity))
            if "{{expiry_date}}" in content_list[i]:
                content_list[i] = content_list[i].replace("{{expiry_date}}", str(license.expiry_date.strftime("%Y-%m-%d")
))

        template = template.format(*content_list)
        return template