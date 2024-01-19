import smtplib
import tkinter as tk
import pandas as pd
from smtplib import SMTP_SSL as SMTP
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from tkinter import filedialog

# pip install pandas openpyxl

def open_text_file_dialog(entry_widget):
    file_path = filedialog.askopenfilename(title="选择文件", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    entry_widget.delete("1.0", tk.END)  
    entry_widget.insert(tk.END, read_file_content(file_path))  

def read_file_content(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            return content
    except Exception as e:
        print(f"读取文件失败: {e}")
        return ""


def choose_file(title):
    root = tk.Tk()
    root.withdraw()  

    file_path = filedialog.askopenfilename(title = title, filetypes=[("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")])

    if file_path:
        return file_path
    else:
        print("error")
        return



def send_email(subject, body, to_email, pass_word, attachment_path):
    
    ######## BUG ########
    from_email = "tommy.chen@unicomnz.com"
    try:
        
        body_part = MIMEText('hi' + to_email + body)
        
        
        with open(attachment_path, "rb") as attachment:
    # Add the attachment to the message
            attachment_part = MIMEBase("application", "octet-stream")
            attachment_part.set_payload(attachment.read())
            encoders.encode_base64(attachment_part)
            attachment_part.add_header(
            "Content-Disposition",
            f"attachment; filename= 'attachment.xlsx'",
            )
            
        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = from_email
        message["To"] = to_email
        message.attach(body_part)
        message.attach(attachment_part)
        
        
        mailserver = smtplib.SMTP('smtp.office365.com', 587) 
        mailserver.set_debuglevel(1)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.ehlo()
        mailserver.login(from_email,pass_word)
        mailserver.sendmail(from_email,to_email,message.as_string())
        mailserver.quit()
        print(f"邮件给 {to_email} 发送成功\n\n\n")
        
    except Exception as e:
        print(f'给 {to_email} 的邮件发送失败: ', e)


def send_emails(to_emails, subject, body, pass_word, attachment_path):
    for to_email in to_emails:
        send_email(subject, body, to_email, pass_word, attachment_path)
    
def open_file_dialog(entry_widget):
    file_path = filedialog.askopenfilename(title="选择文件", filetypes=[("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")])
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, file_path)

def get_emails_list(file_path):
    df = pd.read_excel(file_path)
    column_index = 2  
    to_emails = df.iloc[:, column_index].tolist()
    return to_emails

def send_email_gui():
    root = tk.Tk()
    root.title("邮件发送器")
    tk.Label(root, text="发送邮箱:").grid(row=0, column=0, padx=10, pady=5)
    from_email_entry = tk.Entry(root)
    from_email_entry.grid(row=0, column=1, padx=10, pady=5)


    tk.Label(root, text="密码:").grid(row=1, column=0, padx=10, pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(root, text="收件人列表文件:").grid(row=2, column=0, padx=10, pady=5)
    recipient_file_entry = tk.Entry(root)
    recipient_file_entry.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(root, text="选择文件", command=lambda: open_file_dialog(recipient_file_entry)).grid(row=2, column=2, padx=10, pady=5)

    tk.Label(root, text="附件文件:").grid(row=3, column=0, padx=10, pady=5)
    attachment_file_entry = tk.Entry(root)
    attachment_file_entry.grid(row=3, column=1, padx=10, pady=5)
    tk.Button(root, text="选择文件", command=lambda: open_file_dialog(attachment_file_entry)).grid(row=3, column=2, padx=10, pady=5)

    tk.Label(root, text="标题:").grid(row=4, column=0, padx=10, pady=5)
    title_entry = tk.Entry(root)
    title_entry.grid(row=4, column=1, padx=10, pady=5)


    body_entry = tk.Text(root,wrap="word", width=50, height=20)
    body_entry.grid(row=5, column=1,padx=10, pady=10)


    open_button = tk.Button(root, text="选择文件插入内容(txt)", command=lambda: open_text_file_dialog(body_entry))
    open_button.grid(row=5, column=2,padx=10, pady=10)


    tk.Button(root, text="发送邮件", command=lambda: send_emails(
        subject=title_entry.get(),
        body=body_entry.get("1.0", tk.END).strip(),
        to_emails = get_emails_list(recipient_file_entry.get()),
        pass_word=password_entry.get(),
        attachment_path=attachment_file_entry.get()
    )).grid(row=6, column=0, columnspan=3, pady=10)

    root.mainloop()

send_email_gui()

#email_subject = "Test"
#email_body = "test content"
#file_path = choose_file("选择收件人列表")
#atteachment_path = choose_file("选择附件")


#send_emails(to_emails, email_subject, email_body, pass_word, atteachment_path)
