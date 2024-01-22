from email_job_creater import EmailJobCreater
from create_email_content import EmailWriter


email_job_creater = EmailJobCreater()
email_job_creater.create_email_jobs()
email = EmailWriter()

for company in email_job_creater.companies:
    email.get_template_content()
    email.insert_email_content(company)
    print("=====================================")
    print(email.email_content)
    print("=====================================")
    print()
    print()
    print()

