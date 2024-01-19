import tkinter as tk
import pandas as pd
from tkinter import filedialog
class ExcelReader:
    
    def __init__(self):
        self.info_df = None
        self.email_df = None
        self.info_file_path = self.choose_file("选择License文件")
        self.email_file_path = self.choose_file("选择公司邮箱文件")
        self.read_files()
    
    def choose_file(self, title):
        root = tk.Tk()
        root.withdraw()  
        file_path = filedialog.askopenfilename(title = title, filetypes=[("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")])
        if file_path:
            return  file_path
        else:
            print("error")

    def read_files(self):
        self.info_df = pd.read_excel(self.info_file_path)
        self.email_df = pd.read_excel(self.email_file_path)
        print(self.info_df)
        print(self.email_df)