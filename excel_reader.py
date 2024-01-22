import tkinter as tk
import pandas as pd
from tkinter import filedialog
class ExcelReader:
    
    def __init__(self,email_file_path,info_file_path):
        self.info_df = None
        self.email_df = None
        self.info_file_path = info_file_path
        self.email_file_path = email_file_path
        self.read_files()
    
    def read_files(self):
        self.info_df = pd.read_excel(self.info_file_path)
        self.email_df = pd.read_excel(self.email_file_path)
        print(self.info_df)
        print(self.email_df)