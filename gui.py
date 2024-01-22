
import tkinter as tk
from tkinter import filedialog
from tkinter.font import Font
from tkinter import messagebox
from email_job_creater import EmailJobCreater
from create_email_content import EmailWriter
from email_sender import EmailSender


def open_file_dialog(entry_widget, file_types, ):
    file_path = filedialog.askopenfilename(title = "选择文件", filetypes = file_types)
    entry_widget.delete(0, tk.END)  
    entry_widget.insert(tk.END, file_path) 
    return file_path


def send_email_gui():
    root = tk.Tk()
    font = Font(size=16,weight="bold")
    root.title("邮件发送器")
    tk.Label(root, text="发送邮箱:",width=20,height=3,font= font).grid(row=0, column=0, padx=10, pady=5)
    from_email_entry = tk.Entry(root,width=30,font= font)
    from_email_entry.grid(row=0, column=1, padx=10, pady=5)


    tk.Label(root, text="密码:",width=20,height=3,font= font).grid(row=1, column=0, padx=10, pady=5)
    password_entry = tk.Entry(root, show="*",width=30,font= font)
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(root, text="License信息文件:",width=20,height=3,font= font).grid(row=2, column=0, padx=10, pady=5)
    license_file_entry = tk.Entry(root,width=30,font= font)
    license_file_entry.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(root, text="选择文件", command=lambda: open_file_dialog(license_file_entry,[("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")],)).grid(row=2, column=2, padx=10, pady=5)

    tk.Label(root, text="email列表文件:",width=20,height=3,font= font).grid(row=3, column=0, padx=10, pady=5)
    email_file_entry = tk.Entry(root,width=30,font= font)
    email_file_entry.grid(row=3, column=1, padx=10, pady=5)
    tk.Button(root, text="选择文件", command=lambda: open_file_dialog(email_file_entry,[("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")],)).grid(row=3, column=2, padx=10, pady=5)

    tk.Label(root, text="内容模板文件:",width=20,height=3,font= font).grid(row=4, column=0, padx=10, pady=5)
    content_file_entry = tk.Entry(root,width=30,font= font)
    content_file_entry.grid(row=4, column=1, padx=10, pady=5)
    tk.Button(root, text="选择文件", command=lambda: open_file_dialog(content_file_entry,[("Text files", "*.txt"), ("All files", "*.*")],)).grid(row=4, column=2, padx=10, pady=5)

    tk.Label(root, text="附件文件:",width=20,height=3,font= font).grid(row=5, column=0, padx=10, pady=5)
    attachment_file_entry = tk.Entry(root,width=30,font= font)
    attachment_file_entry.grid(row=5, column=1, padx=10, pady=5)
    tk.Button(root, text="选择文件", command=lambda: open_file_dialog(attachment_file_entry,[("All files", "*.*")],)).grid(row=5, column=2, padx=10, pady=5)

    tk.Label(root, text="标题:",width=20,height=3,font= font).grid(row=6, column=0, padx=10, pady=5)
    title_entry = tk.Entry(root,width=30,font= font)
    title_entry.grid(row=6, column=1, padx=10, pady=5)

    tk.Button(root, text="生成测试邮件",width=20,height=3,font= font, command=lambda: create_test_content(
        root,
        license_file_entry.get(),
        email_file_entry.get(),
        content_file_entry.get(),
        title_entry.get()
        )).grid(row=7, column=0, columnspan=3, pady=10)
        
    tk.Button(root, text="发送邮件",width=20,height=3,font= font, command=lambda: send_email_confirmation_dialog(
        root,
        from_email_entry.get(),
        password_entry.get(),
        license_file_entry.get(),
        email_file_entry.get(),
        content_file_entry.get(),
        title_entry.get(),
        attachment_file_entry.get()
        )).grid(row=8, column=0, columnspan=3, pady=10)
        


    #tk.Button(root, text="发送邮件", command=lambda: ()(
    #    subject=title_entry.get(),
    #    body=body_entry.get("1.0", tk.END).strip(),
    #    pass_word=password_entry.get(),
    #    attachment_path=attachment_file_entry.get()
    #)).grid(row=6, column=0, columnspan=3, pady=10)

    root.mainloop()
    

def display_email_content(root,email_content,title_entry):
    custom_messagebox = tk.Toplevel(root)
    custom_messagebox.title(title_entry)
    custom_messagebox.geometry("800x400")
    content_label = tk.Label(custom_messagebox, text=email_content,anchor="w", justify="left")
    content_label.pack()
    
def create_test_content(root,license_file_entry,email_file_entry,content_file_entry,title_entry):
    email_job_creater = EmailJobCreater()
    email_job_creater.create_email_jobs(email_file_entry,license_file_entry)
    for company in email_job_creater.companies:
        email_writer = EmailWriter(content_file_entry)
        email_writer.insert_email_content(company)
        display_email_content(root,email_writer.email_content,title_entry)
    
    
def create_email_content_and_send(root, from_email,pass_word,license_file_entry,email_file_entry,content_file_entry,title_entry,attachment_file_entry):
    email_job_creater = EmailJobCreater()
    email_sender = EmailSender()
    email_job_creater.create_email_jobs(email_file_entry,license_file_entry)
    for company in email_job_creater.companies:
        email_writer = EmailWriter(content_file_entry)
        email_writer.insert_email_content(company)
        email_sender.send_email(title_entry,email_writer.email_content,from_email,company.email,pass_word,attachment_file_entry)
    messagebox.showinfo("提示", "共" + str(email_sender.success) + "邮件发送成功\n" + str(email_sender.fail) + "邮件发送失败")

def send_email_confirmation_dialog(root, from_email,pass_word,license_file_entry,email_file_entry,content_file_entry,title_entry,attachment_file_entry):
    result = messagebox.askyesno("确认", "您确定要发送邮件吗？")
    
    if result:
        create_email_content_and_send(root, from_email,pass_word,license_file_entry,email_file_entry,content_file_entry,title_entry,attachment_file_entry)
    else:
        return

