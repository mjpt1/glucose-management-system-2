import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import csv
import datetime
import os

# نام فایل برای ذخیره اطلاعات
FILENAME = "blood_pressure_log_gui.csv"
# ستون‌های فایل CSV
FIELDNAMES = ['timestamp', 'systolic', 'diastolic', 'pulse', 'notes', 'category']

# --- بخش منطق داده‌ها (مشابه نسخه قبلی با تغییرات جزئی) ---
def get_blood_pressure_category(systolic, diastolic):
    """
    فشار خون را بر اساس مقادیر سیستولیک و دیاستولیک دسته‌بندی می‌کند.
    """
    if not isinstance(systolic, (int, float)) or not isinstance(diastolic, (int, float)):
        return "مقادیر نامعتبر" # برای جلوگیری از خطا در GUI اگر ورودی عدد نباشد

    if systolic < 90 or diastolic < 60:
        return "فشار خون پایین ( Hypotension )"
    elif systolic < 120 and diastolic < 80:
        return "نرمال ( Normal )"
    elif 120 <= systolic <= 129 and diastolic < 80:
        return "بالا رفته ( Elevated )"
    elif 130 <= systolic <= 139 or 80 <= diastolic <= 89:
        return "فشار خون بالا - مرحله 1 ( Hypertension Stage 1 )"
    elif 140 <= systolic <= 179 or 90 <= diastolic <= 119:
        return "فشار خون بالا - مرحله 2 ( Hypertension Stage 2 )"
    elif systolic >= 180 or diastolic >= 120:
        return "بحران فشار خون ( Hypertensive Crisis ) - فوراً به پزشک مراجعه کنید!"
    else:
        return "دسته‌بندی نامشخص ( لطفاً مقادیر را بررسی کنید )"

def initialize_file():
    """
    اگر فایل CSV وجود نداشته باشد، آن را با سرستون‌ها ایجاد می‌کند.
    """
    if not os.path.exists(FILENAME):
        try:
            with open(FILENAME, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
                writer.writeheader()
            print(f"فایل {FILENAME} ایجاد شد.") # برای لاگ در کنسول، اگر اجرا شود
        except IOError as e:
            messagebox.showerror("خطای فایل", f"امکان ایجاد فایل {FILENAME} وجود ندارد: {e}")


def load_data():
    """
    اطلاعات را از فایل CSV بارگذاری می‌کند.
    """
    initialize_file()
    records = []
    try:
        with open(FILENAME, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # تبدیل مقادیر عددی
                for key in ['systolic', 'diastolic', 'pulse']:
                    if row.get(key) and row[key] != "ثبت نشده": # بررسی وجود کلید و مقدار
                        try:
                            row[key] = int(row[key])
                        except (ValueError, TypeError):
                            row[key] = row[key] # اگر قابل تبدیل نیست، همان رشته بماند
                    elif row.get(key) == "ثبت نشده":
                        pass # مقدار "ثبت نشده" را به همان صورت نگه دار
                    else:
                        row[key] = None # اگر کلید وجود نداشت
                records.append(row)
    except FileNotFoundError:
        messagebox.showinfo("اطلاعات", f"فایل {FILENAME} یافت نشد، یک فایل جدید ایجاد خواهد شد.")
    except Exception as e:
        messagebox.showerror("خطای بارگذاری", f"خطا در بارگذاری اطلاعات از فایل: {e}")
    return records

def save_data(records):
    """
    تمام اطلاعات را در فایل CSV ذخیره می‌کند.
    """
    try:
        with open(FILENAME, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(records)
    except IOError as e:
        messagebox.showerror("خطای ذخیره‌سازی", f"امکان ذخیره اطلاعات در فایل {FILENAME} وجود ندارد: {e}")

# --- کلاس اصلی برنامه گرافیکی ---
class BloodPressureApp:
    def __init__(self, root_window):
        self.root = root_window
        self.mohsen_name = "محسن"
        self.mohsen_website = "mahsen81.ir"
        self.root.title(f"برنامه ثبت فشار خون - {self.mohsen_name} ({self.mohsen_website})")
        self.root.geometry("950x600") # اندازه اولیه پنجره

        # تنظیمات فونت و استایل
        self.font_style = ("Tahoma", 10)
        self.font_style_bold = ("Tahoma", 10, "bold")
        style = ttk.Style()
        style.configure("Treeview.Heading", font=self.font_style_bold)
        style.configure("Treeview", font=self.font_style, rowheight=25) # ارتفاع ردیف
        style.configure("TButton", font=self.font_style)
        style.configure("TLabel", font=self.font_style)
        style.configure("TEntry", font=self.font_style)


        self.blood_pressure_data = load_data()

        # --- فریم ورودی اطلاعات ---
        input_frame = ttk.LabelFrame(self.root, text="ثبت رکورد جدید", padding=(10, 5))
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="فشار سیستولیک (بالا):", font=self.font_style).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.systolic_entry = ttk.Entry(input_frame, width=10, font=self.font_style)
        self.systolic_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="فشار دیاستولیک (پایین):", font=self.font_style).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.diastolic_entry = ttk.Entry(input_frame, width=10, font=self.font_style)
        self.diastolic_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="ضربان قلب:", font=self.font_style).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.pulse_entry = ttk.Entry(input_frame, width=10, font=self.font_style)
        self.pulse_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(input_frame, text="(اختیاری)", font=("Tahoma", 8)).grid(row=1, column=2, padx=0, pady=5, sticky="w")


        ttk.Label(input_frame, text="یادداشت:", font=self.font_style).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.notes_entry = ttk.Entry(input_frame, width=40, font=self.font_style)
        self.notes_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        self.add_button = ttk.Button(input_frame, text="ثبت رکورد", command=self.add_reading_gui, style="TButton")
        self.add_button.grid(row=3, column=0, columnspan=4, padx=5, pady=10)

        self.status_label = ttk.Label(input_frame, text="", font=self.font_style, foreground="blue")
        self.status_label.grid(row=4, column=0, columnspan=4, padx=5, pady=5)


        # --- فریم نمایش اطلاعات (جدول) ---
        display_frame = ttk.LabelFrame(self.root, text="اطلاعات ثبت شده", padding=(10,5))
        display_frame.pack(padx=10, pady=10, fill="both", expand=True)

        cols = ('timestamp', 'systolic', 'diastolic', 'pulse', 'category', 'notes')
        self.tree = ttk.Treeview(display_frame, columns=cols, show='headings', style="Treeview")

        col_widths = {'timestamp': 140, 'systolic': 70, 'diastolic': 70, 'pulse': 70, 'category': 300, 'notes': 250}
        col_align = {'systolic':'center', 'diastolic':'center', 'pulse':'center'}

        for col_name in cols:
            self.tree.heading(col_name, text=self.get_persian_header(col_name))
            self.tree.column(col_name, width=col_widths.get(col_name,100), anchor=col_align.get(col_name, 'w'))


        # اسکرول بارها
        vsb = ttk.Scrollbar(display_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        hsb = ttk.Scrollbar(display_frame, orient="horizontal", command=self.tree.xview)
        hsb.pack(side='bottom', fill='x')

        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(fill="both", expand=True)

        # دکمه حذف رکورد انتخاب شده
        self.delete_button = ttk.Button(display_frame, text="حذف رکورد انتخاب شده", command=self.delete_selected_reading, style="TButton")
        self.delete_button.pack(pady=5)


        self.populate_treeview() # بارگذاری اولیه اطلاعات در جدول

        # --- منو ---
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="بارگذاری مجدد داده‌ها", command=self.refresh_data)
        filemenu.add_separator()
        filemenu.add_command(label="خروج", command=self.root.quit)
        menubar.add_cascade(label="فایل", menu=filemenu)
        self.root.config(menu=menubar)


    def get_persian_header(self, col_name):
        headers = {
            'timestamp': 'تاریخ و زمان',
            'systolic': 'سیستولیک',
            'diastolic': 'دیاستولیک',
            'pulse': 'ضربان',
            'notes': 'یادداشت',
            'category': 'دسته‌بندی فشار'
        }
        return headers.get(col_name, col_name.capitalize())


    def add_reading_gui(self):
        systolic_str = self.systolic_entry.get()
        diastolic_str = self.diastolic_entry.get()
        pulse_str = self.pulse_entry.get()
        notes = self.notes_entry.get().strip()

        if not systolic_str or not diastolic_str:
            messagebox.showerror("خطای ورودی", "فشار سیستولیک و دیاستولیک نمی‌توانند خالی باشند.")
            self.status_label.config(text="خطا: فیلدهای سیستولیک و دیاستولیک اجباری هستند.", foreground="red")
            return

        try:
            systolic = int(systolic_str)
            diastolic = int(diastolic_str)
        except ValueError:
            messagebox.showerror("خطای ورودی", "فشار سیستولیک و دیاستولیک باید عدد باشند.")
            self.status_label.config(text="خطا: مقادیر فشار باید عدد باشند.", foreground="red")
            return

        if not (50 <= systolic <= 300):
            messagebox.showerror("خطای ورودی", "مقدار سیستولیک باید بین 50 تا 300 باشد.")
            self.status_label.config(text="خطا: مقدار سیستولیک نامعتبر.", foreground="red")
            return
        if not (30 <= diastolic <= 200):
            messagebox.showerror("خطای ورودی", "مقدار دیاستولیک باید بین 30 تا 200 باشد.")
            self.status_label.config(text="خطا: مقدار دیاستولیک نامعتبر.", foreground="red")
            return
        if diastolic >= systolic:
            messagebox.showerror("خطای ورودی", "فشار دیاستولیک باید کمتر از سیستولیک باشد.")
            self.status_label.config(text="خطا: دیاستولیک باید کمتر از سیستولیک باشد.", foreground="red")
            return

        pulse = "ثبت نشده"
        if pulse_str:
            try:
                p_val = int(pulse_str)
                if 0 <= p_val <= 250:
                    pulse = p_val
                else:
                    messagebox.showwarning("ورودی ضربان", "ضربان قلب خارج از محدوده معتبر است، ثبت نشد.")
                    self.status_label.config(text="هشدار: ضربان قلب خارج از محدوده، ثبت نشد.", foreground="orange")
            except ValueError:
                messagebox.showwarning("ورودی ضربان", "مقدار ضربان قلب باید عدد باشد، ثبت نشد.")
                self.status_label.config(text="هشدار: ضربان قلب نامعتبر، ثبت نشد.", foreground="orange")


        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        category = get_blood_pressure_category(systolic, diastolic)

        new_record = {
            'timestamp': timestamp,
            'systolic': systolic,
            'diastolic': diastolic,
            'pulse': pulse,
            'notes': notes if notes else "ندارد",
            'category': category
        }

        self.blood_pressure_data.append(new_record)
        save_data(self.blood_pressure_data)
        self.populate_treeview()

        # پاک کردن فیلدهای ورودی
        self.systolic_entry.delete(0, tk.END)
        self.diastolic_entry.delete(0, tk.END)
        self.pulse_entry.delete(0, tk.END)
        self.notes_entry.delete(0, tk.END)
        self.systolic_entry.focus() # فوکوس روی اولین فیلد

        self.status_label.config(text=f"رکورد با موفقیت ثبت شد. وضعیت: {category}", foreground="green")
        if "بحران" in category:
            messagebox.showwarning("هشدار جدی!", f"وضعیت فشار خون: {category}\nفوراً به پزشک مراجعه کنید!")


    def populate_treeview(self):
        # پاک کردن رکوردهای قبلی از جدول
        for i in self.tree.get_children():
            self.tree.delete(i)

        # افزودن رکوردهای جدید (از آخر به اول برای نمایش جدیدترین‌ها در بالا)
        for record in reversed(self.blood_pressure_data):
            values = (
                record.get('timestamp', ''),
                record.get('systolic', ''),
                record.get('diastolic', ''),
                record.get('pulse', ''),
                record.get('category', ''),
                record.get('notes', '')
            )
            self.tree.insert('', tk.END, values=values, iid=record.get('timestamp')) # timestamp به عنوان iid

    def delete_selected_reading(self):
        selected_items = self.tree.selection() # می‌تواند چندین آیتم انتخاب شده را برگرداند
        if not selected_items:
            messagebox.showinfo("اطلاعات", "هیچ رکوردی برای حذف انتخاب نشده است.")
            return

        # در این برنامه ما فقط اجازه انتخاب یک رکورد را با کلیک می‌دهیم، پس selected_items[0] کافیست
        selected_item_iid = selected_items[0] # iid همان timestamp است که هنگام insert دادیم

        confirm = messagebox.askyesno("تایید حذف", f"آیا از حذف رکورد با زمان '{selected_item_iid}' مطمئن هستید؟")
        if confirm:
            # پیدا کردن و حذف رکورد از self.blood_pressure_data
            # timestamp به عنوان شناسه یکتا استفاده شده است.
            self.blood_pressure_data = [r for r in self.blood_pressure_data if r.get('timestamp') != selected_item_iid]
            save_data(self.blood_pressure_data)
            self.populate_treeview() # به روز رسانی جدول
            self.status_label.config(text=f"رکورد '{selected_item_iid}' با موفقیت حذف شد.", foreground="blue")

    def refresh_data(self):
        self.blood_pressure_data = load_data()
        self.populate_treeview()
        self.status_label.config(text="اطلاعات از فایل بارگذاری مجدد شد.", foreground="blue")
        messagebox.showinfo("بارگذاری مجدد", "اطلاعات با موفقیت از فایل خوانده شد.")


if __name__ == "__main__":
    # برای اطمینان از ایجاد فایل لاگ اولیه
    initialize_file()

    main_window = tk.Tk()
    app = BloodPressureApp(main_window)
    main_window.mainloop()
