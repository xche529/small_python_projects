from company import Company
from company import License
from excel_reader import ExcelReader
import pandas as pd
from datetime import datetime


class EmailJobCreater:
    def __init__(self):
        #在这个范围内过期的license会被提醒
        self.days_before_expiry = 62
        #到期时间是第几列（第一列是0）
        self.expiry_date_column_index = 5
        
        self.email_file_company_name_column_index = 0
        
        self.info_file_company_name_column_index = 0
        self.companies = []
        
    def add_company(self, new_company):
        is_new_company = True
        for company in self.companies:
            if company.name == new_company.name:
                company.add_license(new_company.license)
                is_new_company = False
        if is_new_company:
            self.companies.append(new_company)
                
    def create_email_jobs(self):
        excel_reader = ExcelReader()
        current_timestamp = pd.Timestamp("now")
        for info_row_index in range(excel_reader.info_df.shape[0]):
            print(excel_reader.info_df.iloc[info_row_index , self.expiry_date_column_index])
            time_before_expiry = excel_reader.info_df.iloc[info_row_index , self.expiry_date_column_index] - current_timestamp
            seconds_difference = time_before_expiry.total_seconds()
            days_difference = seconds_difference / (24 * 3600)
            print(days_difference)
            #如果license过期了，就不提醒
            if self.days_before_expiry>days_difference:
                if days_difference> 0:
                    target_company_code = excel_reader.info_df.iloc[info_row_index , self.info_file_company_name_column_index]
                    for email_row_index in range(excel_reader.email_df.shape[0]):
                        company_str = excel_reader.email_df.iloc[email_row_index , self.email_file_company_name_column_index]
                        company_code = self.get_company_code(company_str)
                        print(company_code)

    
    def get_company_code(self, company_str):
        company_code = company_str.strip().split()[0]
        return company_code
                    
                    
                
            

            
email_job_creater = EmailJobCreater()
email_job_creater.create_email_jobs()