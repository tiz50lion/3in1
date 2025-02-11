import hashlib
import time
import requests
import json
from tkinter import Tk, Label, Entry, Button, Text, filedialog, messagebox
from tkinter.ttk import Progressbar
from termcolor import colored
from threading import Thread

# Function to create headers
def create_headers(api_key, api_pwd):
    timestamp = int(time.time())
    s = f"{api_key}{api_pwd}{timestamp}"
    sign = hashlib.md5(s.encode('UTF-8')).hexdigest()
    return {
        'Content-Type': 'application/json;charset=utf-8',
        'Sign': sign,
        'Timestamp': str(timestamp),
        'Api-Key': api_key
    }

# Function to fetch the balance
def get_balance(api_key, api_pwd):
    headers = create_headers(api_key, api_pwd)
    url = "https://api.onbuka.com/v3/getBalance"
    try:
        rsp = requests.get(url, headers=headers)
        if rsp.status_code == 200:
            res = json.loads(rsp.text)
            return str(float(res.get("balance", "0")) * 1.11)
        else:
            return "error fetching balance..."
    except Exception as e:
        return "error fetching balance..."



# Function to send SMS to a batch of numbers
def send_batch_sms(api_key, api_pwd, appid, numbers_batch, content, progress, total_batches, batch_index, status_label, total_numbers):
    headers = create_headers(api_key, api_pwd)
    url = "https://api.onbuka.com/v3/sendSms"
    numbers_str = ','.join(numbers_batch)
    body = {"appId": appid, "numbers": numbers_str, "content": content, "senderId": ""}
    try:
        rsp = requests.post(url, json=body, headers=headers)
        if rsp.status_code == 200:
            for number in numbers_batch:
                print(colored(f"[+] =======> {number} [sent]", 'green'))
        else:
            for number in numbers_batch:
                print(colored(f"{number} failed", 'red'))
    except Exception as e:
        for number in numbers_batch:
            print(colored(f"{number} failed - {e}", 'red'))

    sent_count = (batch_index + 1) * len(numbers_batch)
    status_label.config(text=f"Numbers Sent: {sent_count}/{total_numbers}")
    progress['value'] = (batch_index + 1) / total_batches * 100
    progress.update_idletasks()

# Function to send SMS to multiple numbers in batches
def send_sms(api_key, api_pwd, appid, numbers, content, progress, status_label):
    number_list = numbers.split(',')
    total_numbers = len(number_list)
    batches = [number_list[i:i + 20] for i in range(0, len(number_list), 20)]
    total_batches = len(batches)

    for batch_index, batch in enumerate(batches):
        send_batch_sms(api_key, api_pwd, appid, batch, content, progress, total_batches, batch_index, status_label, total_numbers)

# Function to handle file upload
def upload_file(entry_widget):
    file_path = filedialog.askopenfilename()
    if file_path:
        with open(file_path, "r") as file:
            numbers = file.read().replace('\n', ',')
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, numbers)
            count = len(numbers.split(','))
            messagebox.showinfo("Numbers Uploaded", f"Total numbers uploaded: {count}")

# Function to Check License Key
def check_license(license_key_entry, send_button, api_key, api_pwd, appid, numbers_entry, content_text, sms_progress, status_label):
    if license_key_entry.get() == "Anonymous123$":
        send_button['state'] = 'normal'
        send_button.config(bg='green', fg='white', font=('Helvetica', '9', 'bold'))
        # Set the command for the Send SMS button
        send_button.config(command=lambda: Thread(target=send_sms, args=(api_key, api_pwd, appid, numbers_entry.get(), content_text.get("1.0", "end-1c"), sms_progress, status_label)).start())
        messagebox.showinfo("License Verification", "License Key Verified Successfully! \ncontact https://t.me/TizLion for support and more tools")
    else:
        messagebox.showerror("License Verification", "Invalid License Key.\nhttps://t.me/TizLion to purchase key")

# Initialize Second Page
def init_second_page(api_key, api_pwd, appid):
    second_root = Tk()
    second_root.title("Fraud Dept API SENDER")

    global numbers_entry, content_text, send_button

    # Function to update the balance label
    def update_balance_label():
        balance_label.config(text="Fetching balance...")
        balance = get_balance(api_key, api_pwd)
        balance_label.config(text=f"Balance: ${balance}")

    # Fetch and display balance
    balance_label = Label(second_root, text="Fetching balance...", fg='green')
    balance_label.pack()
    update_balance_label()  # Fetch and display balance initially

    # Function to refresh the balance
    def refresh_balance():
        update_balance_label()

    # Refresh Balance Button
    refresh_balance_button = Button(second_root, text="Refresh Balance", command=refresh_balance)
    refresh_balance_button.pack()





    Label(second_root, text="Numbers (comma-separated or upload file):").pack()
    numbers_entry = Entry(second_root, width=50)
    numbers_entry.pack()

    Button(second_root, text="Upload Numbers File", command=lambda: upload_file(numbers_entry)).pack()

    Label(second_root, text="Message Content:").pack()
    content_text = Text(second_root, height=10, width=37)
    content_text.pack()

    Label(second_root, text="License Key:").pack()
    license_key_entry = Entry(second_root, width=50, show="*")
    license_key_entry.pack()

    # Check License Key Button
    check_license_button = Button(second_root, text="Check License Key", command=lambda: check_license(license_key_entry, send_button, api_key, api_pwd, appid, numbers_entry, content_text, sms_progress, status_label))
    check_license_button.pack()

    # Send SMS Button - Initially red and disabled
    send_button = Button(second_root, text="Send SMS", state='disabled', bg='red', fg='white')
    send_button.pack()


    status_label = Label(second_root, text="Numbers Sent: 0/0")
    status_label.pack()

    sms_progress = Progressbar(second_root, orient="horizontal", length=200, mode="determinate")
    sms_progress.pack()

    second_root.mainloop()

# Initialize First Page
def init_first_page():
    root = Tk()
    root.title("F.Dept Server Configuration")

    Label(root, text="API Key:").pack()
    api_key_entry = Entry(root, width=50)
    api_key_entry.pack()

    Label(root, text="API Password:").pack()
    api_pwd_entry = Entry(root, width=50, show="*")
    api_pwd_entry.pack()

    Label(root, text="App ID:").pack()
    appid_entry = Entry(root, width=50)
    appid_entry.pack()

    progress = Progressbar(root, orient="horizontal", length=200, mode="determinate")
    progress.pack()

    def update_progress():
        progress['value'] += 20
        root.update_idletasks()
        if progress['value'] >= 100:
            api_key, api_pwd, appid = api_key_entry.get(), api_pwd_entry.get(), appid_entry.get()
            root.destroy()
            init_second_page(api_key, api_pwd, appid)
        else:
            root.after(600, update_progress)

    connect_button = Button(root, text="Connect to F.Dept Server", command=lambda: Thread(target=update_progress).start())
    connect_button.pack()

    root.mainloop()

# Start Application
init_first_page()