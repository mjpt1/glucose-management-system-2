#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ماژول مربوط به تب‌های مختلف برنامه مدیریت قند خون
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry # type: ignore
import logging
import os
import sys
from datetime import datetime

# افزودن مسیر پروژه به sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Reading, Reminder
from .utils import show_message, validate_persian_date, validate_persian_time, get_glucose_status

logger = logging.getLogger(__name__)

class BaseTab:
    """کلاس پایه برای تب‌های مختلف"""
    def __init__(self, parent, db_manager, config, colors, fonts):
        self.parent = parent
        self.db_manager = db_manager
        self.config = config
        self.colors = colors
        self.fonts = fonts
        self.frame = ttk.Frame(parent, style='TFrame')
        self.create_widgets()

    def create_widgets(self):
        """ایجاد ویجت‌های تب. باید در کلاس‌های فرزند پیاده‌سازی شود."""
        raise NotImplementedError

    def refresh_data(self):
        """بارگذاری مجدد داده‌ها در تب. می‌تواند در کلاس‌های فرزند پیاده‌سازی شود."""
        pass

class MainTab(BaseTab):
    """تب اصلی برای ثبت اطلاعات قند خون"""
    def create_widgets(self):
        """ایجاد ویجت‌های تب اصلی"""
        # فریم اصلی برای محتوا
        content_frame = ttk.Frame(self.frame, style='TFrame')
        content_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # ردیف اول: تاریخ و زمان
        date_time_frame = ttk.Frame(content_frame, style='TFrame')
        date_time_frame.pack(fill=tk.X, pady=5)

        ttk.Label(date_time_frame, text="تاریخ:", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.date_entry = DateEntry(date_time_frame, width=12, background=self.colors['primary'], foreground=self.colors['fg'], borderwidth=2, locale='fa_IR', date_pattern='yyyy/mm/dd')
        self.date_entry.pack(side=tk.RIGHT, padx=5)
        # تنظیم تاریخ پیش‌فرض به امروز
        self.date_entry.set_date(datetime.now())

        ttk.Label(date_time_frame, text="زمان (HH:MM):", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.time_var = tk.StringVar(value=datetime.now().strftime("%H:%M"))
        self.time_entry = ttk.Entry(date_time_frame, textvariable=self.time_var, width=8, style='TEntry', justify=tk.RIGHT)
        self.time_entry.pack(side=tk.RIGHT, padx=5)

        # ردیف دوم: سطح قند خون
        glucose_frame = ttk.Frame(content_frame, style='TFrame')
        glucose_frame.pack(fill=tk.X, pady=5)

        ttk.Label(glucose_frame, text="سطح قند خون (mg/dL):", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.glucose_var = tk.IntVar()
        self.glucose_entry = ttk.Entry(glucose_frame, textvariable=self.glucose_var, width=10, style='TEntry', justify=tk.RIGHT)
        self.glucose_entry.pack(side=tk.RIGHT, padx=5)

        # ردیف سوم: توضیحات
        desc_frame = ttk.Frame(content_frame, style='TFrame')
        desc_frame.pack(fill=tk.X, pady=5)

        ttk.Label(desc_frame, text="توضیحات:", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.desc_entry = ttk.Entry(desc_frame, width=40, style='TEntry', justify=tk.RIGHT)
        self.desc_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        # ردیف چهارم: وضعیت غذا و خلق و خو
        status_mood_frame = ttk.Frame(content_frame, style='TFrame')
        status_mood_frame.pack(fill=tk.X, pady=5)

        ttk.Label(status_mood_frame, text="وضعیت غذا:", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.meal_status_var = tk.StringVar()
        self.meal_status_combo = ttk.Combobox(status_mood_frame, textvariable=self.meal_status_var, 
                                              values=self.config['READING_FIELDS']['meal_status_options'], state="readonly", style='TCombobox', justify=tk.RIGHT)
        self.meal_status_combo.pack(side=tk.RIGHT, padx=5)
        self.meal_status_combo.set(self.config['READING_FIELDS']['meal_status_options'][0])

        ttk.Label(status_mood_frame, text="خلق و خو:", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.mood_var = tk.StringVar()
        self.mood_combo = ttk.Combobox(status_mood_frame, textvariable=self.mood_var, 
                                       values=self.config['READING_FIELDS']['mood_options'], state="readonly", style='TCombobox', justify=tk.RIGHT)
        self.mood_combo.pack(side=tk.RIGHT, padx=5)
        self.mood_combo.set(self.config['READING_FIELDS']['mood_options'][2]) # متوسط

        # ردیف پنجم: سطح استرس و دقایق ورزش
        stress_exercise_frame = ttk.Frame(content_frame, style='TFrame')
        stress_exercise_frame.pack(fill=tk.X, pady=5)

        ttk.Label(stress_exercise_frame, text="سطح استرس (1-10):", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.stress_var = tk.IntVar(value=5)
        self.stress_spinbox = ttk.Spinbox(stress_exercise_frame, from_=1, to=10, textvariable=self.stress_var, width=5, style='TSpinbox', justify=tk.RIGHT)
        self.stress_spinbox.pack(side=tk.RIGHT, padx=5)

        ttk.Label(stress_exercise_frame, text="دقایق ورزش:", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.exercise_var = tk.IntVar(value=0)
        self.exercise_entry = ttk.Entry(stress_exercise_frame, textvariable=self.exercise_var, width=8, style='TEntry', justify=tk.RIGHT)
        self.exercise_entry.pack(side=tk.RIGHT, padx=5)

        # ردیف ششم: ساعات خواب
        sleep_frame = ttk.Frame(content_frame, style='TFrame')
        sleep_frame.pack(fill=tk.X, pady=5)

        ttk.Label(sleep_frame, text="ساعات خواب:", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.sleep_var = tk.DoubleVar(value=8.0)
        self.sleep_entry = ttk.Entry(sleep_frame, textvariable=self.sleep_var, width=8, style='TEntry', justify=tk.RIGHT)
        self.sleep_entry.pack(side=tk.RIGHT, padx=5)

        # دکمه ذخیره
        save_button = ttk.Button(content_frame, text="ذخیره اطلاعات", command=self.save_reading, style='TButton')
        save_button.pack(pady=15)

        # لیبل وضعیت
        self.status_label = ttk.Label(content_frame, text="", style='Status.TLabel') # Assuming Status.TLabel is defined in create_persian_style
        self.status_label.pack(pady=5)

    def save_reading(self):
        """ذخیره اطلاعات خوانش قند خون در پایگاه داده"""
        try:
            jalali_date_str = self.date_entry.get_date().strftime("%Y/%m/%d")
            time_str = self.time_var.get()
            glucose_level = self.glucose_var.get()
            description = self.desc_entry.get()
            meal_status = self.meal_status_var.get()
            mood = self.mood_var.get()
            stress_level = self.stress_var.get()
            exercise_minutes = self.exercise_var.get()
            sleep_hours = self.sleep_var.get()

            if not validate_persian_date(jalali_date_str):
                show_message(self.frame, title="خطا", message="فرمت تاریخ نامعتبر است. (مثال: 1402/01/15)", message_type="error")
                return
            
            if not validate_persian_time(time_str):
                show_message(self.frame, title="خطا", message="فرمت زمان نامعتبر است. (مثال: 14:30)", message_type="error")
                return

            if not (0 < glucose_level < 1000): # اعتبارسنجی ساده برای سطح قند
                show_message(self.frame, title="خطا", message="سطح قند خون نامعتبر است.", message_type="error")
                return
            
            # تبدیل تاریخ شمسی به میلادی برای ذخیره در دیتابیس
            # DateEntry به طور پیش‌فرض تاریخ میلادی برمی‌گرداند، پس نیازی به تبدیل دستی نیست اگر از get_date() استفاده شود.
            gregorian_date_obj = self.date_entry.get_date()
            gregorian_date_str = gregorian_date_obj.strftime("%Y-%m-%d")

            reading = Reading(
                user_id=1, # در آینده باید از کاربر فعلی گرفته شود
                gregorian_date=gregorian_date_str,
                jalali_date=jalali_date_str,
                time=time_str,
                glucose_level=glucose_level,
                description=description,
                meal_status=meal_status,
                mood=mood,
                stress_level=stress_level,
                exercise_minutes=exercise_minutes,
                sleep_hours=sleep_hours
            )
            
            self.db_manager.insert_reading(reading)
            show_message(self.frame, title="موفقیت", message="اطلاعات با موفقیت ذخیره شد.", message_type="info")
            self.status_label.config(text=f"آخرین رکورد در {jalali_date_str} - {time_str} ذخیره شد.")
            self.clear_entries()

        except ValueError:
            show_message(self.frame, title="خطا", message="لطفاً مقادیر عددی معتبر وارد کنید.", message_type="error")
            logging.error("خطا در تبدیل مقادیر ورودی در تب اصلی", exc_info=True)
        except Exception as e:
            show_message(self.frame, title="خطا", message=f"خطایی در ذخیره اطلاعات رخ داد: {e}", message_type="error")
            logging.error(f"خطا در ذخیره اطلاعات در تب اصلی: {e}", exc_info=True)

    def clear_entries(self):
        """پاک کردن فیلدهای ورودی پس از ذخیره"""
        self.date_entry.set_date(datetime.now())
        self.time_var.set(datetime.now().strftime("%H:%M"))
        self.glucose_var.set(0)
        self.desc_entry.delete(0, tk.END)
        self.meal_status_combo.set(self.config['READING_FIELDS']['meal_status_options'][0])
        self.mood_combo.set(self.config['READING_FIELDS']['mood_options'][2])
        self.stress_var.set(5)
        self.exercise_var.set(0)
        self.sleep_var.set(8.0)
        self.glucose_entry.focus() # انتقال فوکوس به اولین فیلد مهم

    def refresh_data(self):
        """بارگذاری مجدد داده‌ها (در صورت نیاز)"""
        # در این تب خاص، نیازی به بارگذاری مجدد داده‌ها پس از هر بار نمایش نیست
        # اما می‌توان برای بروزرسانی مقادیر پیش‌فرض یا وضعیت استفاده کرد
        self.status_label.config(text="فرم ثبت اطلاعات آماده است.")
        self.clear_entries()

class ReportTab(BaseTab):
    """تب گزارش‌ها"""
    def create_widgets(self):
        """ایجاد ویجت‌های تب گزارش‌ها"""
        # فریم اصلی برای محتوا
        content_frame = ttk.Frame(self.frame, style='TFrame')
        content_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # فریم فیلترها
        filter_frame = ttk.Frame(content_frame, style='TFrame')
        filter_frame.pack(fill=tk.X, pady=5)

        ttk.Label(filter_frame, text="از تاریخ:", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.start_date_entry = DateEntry(filter_frame, width=12, background=self.colors['primary'], foreground=self.colors['fg'], borderwidth=2, locale='fa_IR', date_pattern='yyyy/mm/dd')
        self.start_date_entry.pack(side=tk.RIGHT, padx=5)
        # self.start_date_entry.set_date(datetime.now() - timedelta(days=7)) # پیش‌فرض: 7 روز قبل

        ttk.Label(filter_frame, text="تا تاریخ:", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.end_date_entry = DateEntry(filter_frame, width=12, background=self.colors['primary'], foreground=self.colors['fg'], borderwidth=2, locale='fa_IR', date_pattern='yyyy/mm/dd')
        self.end_date_entry.pack(side=tk.RIGHT, padx=5)
        self.end_date_entry.set_date(datetime.now()) # پیش‌فرض: امروز

        filter_button = ttk.Button(filter_frame, text="اعمال فیلتر", command=self.load_report_data, style='TButton')
        filter_button.pack(side=tk.RIGHT, padx=10)

        # Treeview برای نمایش گزارش
        self.report_tree = ttk.Treeview(content_frame, style='Treeview')
        self.report_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # تعریف ستون‌ها
        columns = self.config['REPORT_TAB_COLUMNS']
        self.report_tree["columns"] = [col['id'] for col in columns]
        self.report_tree["show"] = "headings"  # عدم نمایش ستون خالی اولیه

        for col in columns:
            self.report_tree.heading(col['id'], text=col['name'], anchor=tk.E if col.get('align_right', True) else tk.W)
            self.report_tree.column(col['id'], width=col['width'], anchor=tk.E if col.get('align_right', True) else tk.W)
        
        # اضافه کردن اسکرول بار
        scrollbar = ttk.Scrollbar(self.report_tree, orient=tk.VERTICAL, command=self.report_tree.yview, style='Vertical.TScrollbar')
        self.report_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        # بارگذاری اولیه داده‌ها
        self.load_report_data()

    def load_report_data(self):
        """بارگذاری و نمایش داده‌های گزارش بر اساس فیلتر تاریخ"""
        try:
            start_date_obj = self.start_date_entry.get_date()
            end_date_obj = self.end_date_entry.get_date()

            if not start_date_obj or not end_date_obj:
                show_message(self.frame, title="توجه", message="لطفا تاریخ شروع و پایان را انتخاب کنید.", message_type="warning")
                return

            start_date_str = start_date_obj.strftime("%Y-%m-%d")
            end_date_str = end_date_obj.strftime("%Y-%m-%d")

            if start_date_obj > end_date_obj:
                show_message(self.frame, title="خطا", message="تاریخ شروع نمی‌تواند بعد از تاریخ پایان باشد.", message_type="error")
                return

            # پاک کردن داده‌های قبلی
            for item in self.report_tree.get_children():
                self.report_tree.delete(item)
            
            readings = self.db_manager.fetch_readings_by_date_range(start_date_str, end_date_str)
            
            if not readings:
                show_message(self.frame, title="اطلاعات", message="هیچ داده‌ای برای محدوده تاریخ انتخاب شده یافت نشد.", message_type="info")
                return

            for reading_obj in readings:
                # تبدیل reading_obj (که یک شی Reading است) به یک تاپل از مقادیر برای Treeview
                # ترتیب مقادیر باید با ترتیب ستون‌ها در self.config['REPORT_TAB_COLUMNS'] مطابقت داشته باشد
                values = (
                    reading_obj.jalali_date,
                    reading_obj.time,
                    reading_obj.glucose_level,
                    get_glucose_status(reading_obj.glucose_level, self.config['GLUCOSE_LEVELS'])['status'],
                    reading_obj.meal_status,
                    reading_obj.mood,
                    reading_obj.stress_level,
                    reading_obj.exercise_minutes,
                    reading_obj.sleep_hours,
                    reading_obj.description
                )
                self.report_tree.insert("", tk.END, values=values)

        except Exception as e:
            show_message(self.frame, title="خطا", message=f"خطایی در بارگذاری گزارش رخ داد: {e}", message_type="error")
            logging.error(f"خطا در بارگذاری گزارش: {e}", exc_info=True)

    def refresh_data(self):
        """بارگذاری مجدد داده‌های گزارش"""
        self.load_report_data()

class ChartTab(BaseTab):
    """تب نمودارها"""
    def create_widgets(self):
        """ایجاد ویجت‌های تب نمودارها"""
        # فریم اصلی برای محتوا
        content_frame = ttk.Frame(self.frame, style='TFrame')
        content_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # فریم کنترل‌ها
        controls_frame = ttk.Frame(content_frame, style='TFrame')
        controls_frame.pack(fill=tk.X, pady=5)

        ttk.Label(controls_frame, text="نوع نمودار:", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.chart_type_var = tk.StringVar(value=self.config.get('DEFAULT_CHART_TYPE', 'نمودار خطی'))
        chart_types = self.config.get('CHART_TYPES', ['نمودار خطی', 'نمودار پراکندگی', 'نمودار میله‌ای'])
        self.chart_type_combo = ttk.Combobox(controls_frame, textvariable=self.chart_type_var, values=chart_types, state="readonly", style='TCombobox', width=15, font=self.fonts['small'])
        self.chart_type_combo.pack(side=tk.RIGHT, padx=5)
        self.chart_type_combo.bind("<<ComboboxSelected>>", self.plot_chart)

        ttk.Label(controls_frame, text="از تاریخ:", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.start_date_entry_chart = DateEntry(controls_frame, width=12, background=self.colors['primary'], foreground=self.colors['fg'], borderwidth=2, locale='fa_IR', date_pattern='yyyy/mm/dd')
        self.start_date_entry_chart.pack(side=tk.RIGHT, padx=5)
        # self.start_date_entry_chart.set_date(datetime.now() - timedelta(days=self.config.get('DEFAULT_CHART_DAYS_RANGE', 7)))

        ttk.Label(controls_frame, text="تا تاریخ:", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.end_date_entry_chart = DateEntry(controls_frame, width=12, background=self.colors['primary'], foreground=self.colors['fg'], borderwidth=2, locale='fa_IR', date_pattern='yyyy/mm/dd')
        self.end_date_entry_chart.pack(side=tk.RIGHT, padx=5)
        self.end_date_entry_chart.set_date(datetime.now())

        filter_button_chart = ttk.Button(controls_frame, text="نمایش نمودار", command=self.plot_chart, style='TButton')
        filter_button_chart.pack(side=tk.RIGHT, padx=10)

        # فریم برای نمودار
        self.chart_frame = ttk.Frame(content_frame, style='TFrame')
        self.chart_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.fig, self.ax = plt.subplots(figsize=self.config.get('CHART_SIZE', (8, 4)), dpi=self.config.get('CHART_DPI', 100))
        self.fig.patch.set_facecolor(self.colors['bg'])
        self.ax.set_facecolor(self.colors['bg'])
        self.ax.tick_params(colors=self.colors['fg'], which='both')
        self.ax.spines['bottom'].set_color(self.colors['fg'])
        self.ax.spines['top'].set_color(self.colors['fg'])
        self.ax.spines['left'].set_color(self.colors['fg'])
        self.ax.spines['right'].set_color(self.colors['fg'])
        self.ax.xaxis.label.set_color(self.colors['fg'])
        self.ax.yaxis.label.set_color(self.colors['fg'])
        self.ax.title.set_color(self.colors['fg'])

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.chart_frame, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        # تغییر رنگ دکمه‌های تولبار
        for button in self.toolbar.winfo_children():
            button.configure(background=self.colors['bg'], foreground=self.colors['fg'])
            if isinstance(button, tk.Button) or isinstance(button, ttk.Button):
                 button.configure(relief=tk.FLAT)
            if hasattr(button, 'config'): # برای سازگاری با نسخه‌های مختلف
                try:
                    button.config(background=self.colors['bg'])
                except tk.TclError:
                    pass # برخی ویجت‌ها ممکن است آپشن background را نداشته باشند

        self.plot_chart() # بارگذاری اولیه نمودار

    def load_chart_data(self):
        """بارگذاری داده‌ها برای نمودار بر اساس فیلتر تاریخ"""
        try:
            start_date_obj = self.start_date_entry_chart.get_date()
            end_date_obj = self.end_date_entry_chart.get_date()

            if not start_date_obj or not end_date_obj:
                # show_message("توجه", "لطفا تاریخ شروع و پایان را برای نمودار انتخاب کنید.", "warning", parent=self.frame)
                return None # یا یک لیست خالی برای جلوگیری از خطا در plot_chart

            start_date_str = start_date_obj.strftime("%Y-%m-%d")
            end_date_str = end_date_obj.strftime("%Y-%m-%d")

            if start_date_obj > end_date_obj:
                show_message(self.frame, title="خطا", message="تاریخ شروع نمودار نمی‌تواند بعد از تاریخ پایان باشد.", message_type="error")
                return None
            
            readings = self.db_manager.fetch_readings_by_date_range(start_date_str, end_date_str)
            return readings
        except Exception as e:
            show_message(self.frame, title="خطا", message=f"خطایی در بارگذاری داده‌های نمودار رخ داد: {e}", message_type="error")
            logging.error(f"خطا در بارگذاری داده‌های نمودار: {e}", exc_info=True)
            return None

    def plot_chart(self, event=None):
        """رسم نمودار بر اساس داده‌های بارگذاری شده و نوع نمودار انتخابی"""
        readings = self.load_chart_data()
        self.ax.clear()

        if not readings:
            self.ax.text(0.5, 0.5, "داده‌ای برای نمایش وجود ندارد", ha='center', va='center', color=self.colors['fg'], fontproperties=get_font(self.fonts['large']['family'], self.fonts['large']['size']))
            self.canvas.draw()
            return

        dates = []
        glucose_levels = []
        for r_obj in readings:
            try:
                # ترکیب تاریخ و زمان برای رسم دقیق‌تر روی محور زمان
                datetime_str = f"{r_obj.date} {r_obj.time}"
                dt_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
                dates.append(dt_obj)
                glucose_levels.append(r_obj.glucose_level)
            except ValueError as ve:
                logging.warning(f"خطا در تبدیل تاریخ/زمان برای نمودار: {r_obj.date} {r_obj.time} - {ve}")
                continue # از این داده صرف نظر کن
        
        if not dates or not glucose_levels:
            self.ax.text(0.5, 0.5, "داده معتبری برای نمایش وجود ندارد", ha='center', va='center', color=self.colors['fg'], fontproperties=get_font(self.fonts['large']['family'], self.fonts['large']['size']))
            self.canvas.draw()
            return

        chart_type = self.chart_type_var.get()
        chart_color = self.config.get('CHART_LINE_COLOR', self.colors.get('accent', 'blue'))

        if chart_type == 'نمودار خطی':
            self.ax.plot(dates, glucose_levels, marker='o', linestyle='-', color=chart_color, markersize=5)
        elif chart_type == 'نمودار پراکندگی':
            self.ax.scatter(dates, glucose_levels, color=chart_color, s=30)
        elif chart_type == 'نمودار میله‌ای':
            # برای نمودار میله‌ای، ممکن است نیاز به پردازش بیشتری روی تاریخ‌ها باشد
            # اینجا یک نمایش ساده ارائه می‌شود.
            # تبدیل تاریخ‌ها به رشته برای برچسب‌های محور x
            str_dates = [d.strftime('%y/%m/%d\n%H:%M') for d in dates]
            self.ax.bar(str_dates, glucose_levels, color=chart_color, width=0.5)
            self.ax.tick_params(axis='x', rotation=45, labelsize=self.fonts['small']['size']-2)
        else:
            self.ax.plot(dates, glucose_levels, marker='o', linestyle='-', color=chart_color)

        self.ax.set_xlabel("تاریخ و زمان", fontproperties=get_font(self.fonts['normal']['family'], self.fonts['normal']['size']), color=self.colors['fg'])
        self.ax.set_ylabel("سطح قند خون (mg/dL)", fontproperties=get_font(self.fonts['normal']['family'], self.fonts['normal']['size']), color=self.colors['fg'])
        self.ax.set_title(f"{chart_type} سطح قند خون", fontproperties=get_font(self.fonts['large']['family'], self.fonts['large']['size']), color=self.colors['fg'])
        
        # قالب‌بندی محور تاریخ‌ها
        if chart_type != 'نمودار میله‌ای': # برای نمودار میله‌ای، برچسب‌ها دستی تنظیم شده‌اند
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M', tz=get_localzone()))
            self.fig.autofmt_xdate() # چرخش خودکار برچسب‌های تاریخ برای خوانایی بهتر

        self.ax.grid(True, linestyle='--', alpha=0.6, color=self.colors.get('grid', '#888888'))
        self.fig.tight_layout() # تنظیم خودکار چیدمان برای جلوگیری از همپوشانی
        self.canvas.draw()

    def refresh_data(self):
        """بارگذاری مجدد داده‌ها و رسم نمودار"""
        self.plot_chart()

class AITab(BaseTab):
    """تب هوش مصنوعی"""
    def __init__(self, parent, db_manager, ai_analyzer, config, colors, fonts):
        self.ai_analyzer = ai_analyzer # آبجکت تحلیلگر هوش مصنوعی
        self.fonts = fonts # اضافه کردن فونت‌ها
        super().__init__(parent, db_manager, config, colors)

    def create_widgets(self):
        """ایجاد ویجت‌های تب هوش مصنوعی"""
        content_frame = ttk.Frame(self.frame, style='TFrame')
        content_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # فریم کنترل‌ها
        controls_frame = ttk.Frame(content_frame, style='TFrame')
        controls_frame.pack(fill=tk.X, pady=10)

        self.analyze_button = ttk.Button(controls_frame, text="شروع تحلیل و پیش‌بینی", command=self.run_ai_analysis, style='Accent.TButton')
        self.analyze_button.pack(pady=10)

        # فریم نمایش نتایج
        results_frame = ttk.LabelFrame(content_frame, text="نتایج تحلیل و پیش‌بینی", style='TLabelframe')
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=15, state=tk.DISABLED, font=self.fonts['normal'], bg=self.colors['light_bg'], fg=self.colors['fg'], relief=tk.FLAT, padx=5, pady=5)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # اضافه کردن اسکرول بار به Text ویجت
        scrollbar = ttk.Scrollbar(self.results_text, orient=tk.VERTICAL, command=self.results_text.yview, style='Vertical.TScrollbar')
        self.results_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        # نمایش پیش‌بینی‌های اخیر (اگر وجود داشته باشد)
        self.load_recent_predictions()

    def run_ai_analysis(self):
        """اجرای تحلیل هوش مصنوعی و نمایش نتایج"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "در حال اجرای تحلیل هوش مصنوعی... لطفاً منتظر بمانید.\n", 'info')
        self.results_text.config(state=tk.DISABLED)
        self.frame.update_idletasks() # برای نمایش پیام بلافاصله

        try:
            min_readings_for_train = self.config.get('AI_MIN_READINGS_FOR_TRAIN', 50)
            all_readings_count = self.db_manager.get_readings_count()
            
            if all_readings_count < min_readings_for_train:
                show_message(self.frame, title="توجه", message=f"برای اجرای تحلیل هوش مصنوعی، حداقل به {min_readings_for_train} داده قند خون نیاز است. تعداد داده‌های فعلی: {all_readings_count}", message_type="warning")
                self.results_text.config(state=tk.NORMAL)
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, f"تعداد داده‌ها برای تحلیل کافی نیست (نیاز به {min_readings_for_train}، موجود: {all_readings_count}).\n", 'error')
                self.results_text.config(state=tk.DISABLED)
                return

            # استفاده از ai_analyzer واقعی
            analysis_result, prediction_obj = self.ai_analyzer.analyze_and_predict()

            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, analysis_result if analysis_result else "تحلیلی برای نمایش وجود ندارد.\n", 'normal_text')
            self.results_text.insert(tk.END, "\n" + "="*30 + "\n\n", 'separator')
            
            if prediction_obj:
                prediction_text = f"پیش‌بینی سطح قند خون: {prediction_obj.predicted_value:.2f} mg/dL (اطمینان: {prediction_obj.confidence_score*100:.1f}%)\nمدل مورد استفاده: {prediction_obj.model_version}\n"
                self.results_text.insert(tk.END, prediction_text, 'prediction')
                # ذخیره پیش‌بینی در دیتابیس از طریق ai_analyzer انجام شده است
            else:
                self.results_text.insert(tk.END, "پیش‌بینی در حال حاضر امکان‌پذیر نیست.\n", 'info')

            self.results_text.config(state=tk.DISABLED)

            # تعریف تگ‌ها برای استایل‌دهی
            self.results_text.tag_configure('info', foreground=self.colors.get('accent', 'blue'), font=self.fonts['normal_bold'])
            self.results_text.tag_configure('error', foreground=self.colors.get('error', 'red'), font=self.fonts['normal_bold'])
            self.results_text.tag_configure('normal_text', foreground=self.colors['fg'], font=self.fonts['normal'])
            self.results_text.tag_configure('separator', foreground=self.colors.get('disabled_fg', 'gray'), font=self.fonts['small'])
            self.results_text.tag_configure('prediction', foreground=self.colors.get('success', 'green'), font=self.fonts['normal_bold'])

            show_message(self.frame, title="موفقیت", message="تحلیل و پیش‌بینی با موفقیت انجام شد.", message_type="info")
            self.load_recent_predictions() # برای نمایش پیش‌بینی جدید

        except Exception as e:
            show_message(self.frame, title="خطا", message=f"خطایی در اجرای تحلیل هوش مصنوعی رخ داد: {e}", message_type="error")
            logging.error(f"خطا در اجرای تحلیل AI: {e}", exc_info=True)
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"خطا در اجرای تحلیل: {e}\n", 'error')
            self.results_text.config(state=tk.DISABLED)

    def load_recent_predictions(self):
        """بارگذاری و نمایش پیش‌بینی‌های اخیر از دیتابیس"""
        try:
            recent_preds = self.db_manager.fetch_recent_predictions(limit=self.config.get('AI_RECENT_PREDICTIONS_DISPLAY_COUNT', 3))
            self.results_text.config(state=tk.NORMAL)
            current_content = self.results_text.get(1.0, tk.END).strip()
            if current_content and not current_content.endswith(("\n", "\r")):
                self.results_text.insert(tk.END, "\n") # اطمینان از وجود خط جدید
            if current_content: # فقط اگر متنی از قبل وجود دارد، جداکننده اضافه کن
                 self.results_text.insert(tk.END, "\n" + "-"*30 + "\n\n", 'separator')
            
            if recent_preds:
                self.results_text.insert(tk.END, "پیش‌بینی‌های اخیر:\n", 'info')
                for pred in recent_preds:
                    try:
                        pred_time_jalali = convert_to_jalali(pred.prediction_time, date_format="%Y-%m-%d %H:%M:%S").strftime("%Y/%m/%d ساعت %H:%M")
                    except ValueError:
                        pred_time_jalali = pred.prediction_time # اگر تبدیل ناموفق بود، همان تاریخ میلادی را نمایش بده
                    pred_info = f"- در تاریخ {pred_time_jalali}: {pred.predicted_value} mg/dL (اطمینان: {pred.confidence_score*100:.1f}%) - مدل: {pred.model_version}\n"
                    self.results_text.insert(tk.END, pred_info, 'normal_text')
            else:
                if not current_content: # فقط اگر خالی است این پیام را نشان بده
                    self.results_text.insert(tk.END, "هیچ پیش‌بینی اخیری برای نمایش وجود ندارد.\n", 'info')
            
            self.results_text.config(state=tk.DISABLED)
        except Exception as e:
            logging.error(f"خطا در بارگذاری پیش‌بینی‌های اخیر: {e}", exc_info=True)

    def refresh_data(self):
        """بارگذاری مجدد داده‌ها (در اینجا پیش‌بینی‌های اخیر)"""
        # ممکن است بخواهیم نتایج تحلیل قبلی را پاک کنیم یا فقط پیش‌بینی‌ها را رفرش کنیم
        # در اینجا فقط پیش‌بینی‌های اخیر را رفرش می‌کنیم و به کاربر اجازه می‌دهیم تحلیل جدید را دستی اجرا کند
        self.load_recent_predictions()

class UserSettingsTab(BaseTab):
    """تب تنظیمات کاربر"""
    def __init__(self, parent, db_manager, config, colors, fonts):
        self.fonts = fonts
        super().__init__(parent, db_manager, config, colors)

    def create_widgets(self):
        """ایجاد ویجت‌های تب تنظیمات کاربر"""
        content_frame = ttk.Frame(self.frame, style='TFrame')
        content_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # فریم برای اطلاعات شخصی
        personal_info_frame = ttk.LabelFrame(content_frame, text="اطلاعات شخصی", style='TLabelframe')
        personal_info_frame.pack(fill=tk.X, pady=10, padx=5)

        # نام کاربری
        ttk.Label(personal_info_frame, text="نام کاربری:", style='TLabel').grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.username_entry = ttk.Entry(personal_info_frame, font=self.fonts['normal'], style='TEntry', width=30)
        self.username_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # سن
        ttk.Label(personal_info_frame, text="سن:", style='TLabel').grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.age_entry = ttk.Entry(personal_info_frame, font=self.fonts['normal'], style='TEntry', width=30)
        self.age_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # جنسیت
        ttk.Label(personal_info_frame, text="جنسیت:", style='TLabel').grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.gender_var = tk.StringVar(value=self.config.get('DEFAULT_GENDER', 'نامشخص'))
        gender_options = ["مرد", "زن", "نامشخص"]
        self.gender_menu = ttk.Combobox(personal_info_frame, textvariable=self.gender_var, values=gender_options, state="readonly", style='TCombobox', width=28, font=self.fonts['normal'])
        self.gender_menu.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        personal_info_frame.grid_columnconfigure(0, weight=1)

        # فریم برای محدوده قند خون هدف
        glucose_target_frame = ttk.LabelFrame(content_frame, text="محدوده قند خون هدف (mg/dL)", style='TLabelframe')
        glucose_target_frame.pack(fill=tk.X, pady=10, padx=5)

        # حداقل قند خون
        ttk.Label(glucose_target_frame, text="حداقل:", style='TLabel').grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.min_glucose_entry = ttk.Entry(glucose_target_frame, font=self.fonts['normal'], style='TEntry', width=30)
        self.min_glucose_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # حداکثر قند خون
        ttk.Label(glucose_target_frame, text="حداکثر:", style='TLabel').grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.max_glucose_entry = ttk.Entry(glucose_target_frame, font=self.fonts['normal'], style='TEntry', width=30)
        self.max_glucose_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        glucose_target_frame.grid_columnconfigure(0, weight=1)

        # دکمه ذخیره
        save_button = ttk.Button(content_frame, text="ذخیره تنظیمات", command=self.save_settings, style='Accent.TButton')
        save_button.pack(pady=10)

        self.load_settings()

    def load_settings(self):
        """بارگذاری تنظیمات فعلی کاربر"""
        try:
            user_settings = self.db_manager.get_user_settings()
            if user_settings:
                self.username_entry.delete(0, tk.END)
                self.username_entry.insert(0, user_settings.username)
                self.age_entry.delete(0, tk.END)
                self.age_entry.insert(0, str(user_settings.age))
                self.gender_var.set(user_settings.gender)
                self.min_glucose_entry.delete(0, tk.END)
                self.min_glucose_entry.insert(0, str(user_settings.target_glucose_min))
                self.max_glucose_entry.delete(0, tk.END)
                self.max_glucose_entry.insert(0, str(user_settings.target_glucose_max))
            else:
                # بارگذاری مقادیر پیش‌فرض از config.py اگر تنظیمات کاربر وجود نداشت
                self.username_entry.insert(0, self.config.get('DEFAULT_USERNAME', 'کاربر جدید'))
                self.age_entry.insert(0, str(self.config.get('DEFAULT_AGE', 30)))
                self.gender_var.set(self.config.get('DEFAULT_GENDER', 'نامشخص'))
                self.min_glucose_entry.insert(0, str(self.config.get('GLUCOSE_LEVELS', {}).get('NORMAL_MIN', 70)))
                self.max_glucose_entry.insert(0, str(self.config.get('GLUCOSE_LEVELS', {}).get('NORMAL_MAX', 140)))
        except Exception as e:
            show_message(self.frame, title="خطا", message=f"خطا در بارگذاری تنظیمات کاربر: {e}", message_type="error")
            logging.error(f"خطا در بارگذاری تنظیمات کاربر: {e}", exc_info=True)

    def save_settings(self):
        """ذخیره تنظیمات کاربر در دیتابیس"""
        username = self.username_entry.get().strip()
        age_str = self.age_entry.get().strip()
        gender = self.gender_var.get()
        min_glucose_str = self.min_glucose_entry.get().strip()
        max_glucose_str = self.max_glucose_entry.get().strip()

        if not username or not age_str or not min_glucose_str or not max_glucose_str:
            show_message(self.frame, title="خطا", message="لطفاً تمام فیلدهای تنظیمات را پر کنید.", message_type="error")
            return

        try:
            age = int(age_str)
            min_glucose = int(min_glucose_str)
            max_glucose = int(max_glucose_str)

            if not (0 < age < 120):
                show_message(self.frame, title="خطا", message="سن باید بین 1 تا 120 باشد.", message_type="error")
                return
            if not (0 < min_glucose < 1000) or not (0 < max_glucose < 1000):
                show_message(self.frame, title="خطا", message="محدوده قند خون باید مقادیر معتبر و مثبت باشد.", message_type="error")
                return
            if min_glucose >= max_glucose:
                show_message(self.frame, title="خطا", message="حداقل قند خون نمی‌تواند بزرگتر یا مساوی حداکثر باشد.", message_type="error")
                return

            self.db_manager.save_user_settings(username, age, gender, min_glucose, max_glucose)
            show_message(self.frame, title="موفقیت", message="تنظیمات با موفقیت ذخیره شد.", message_type="info")
            # به‌روزرسانی مقادیر در config برای استفاده فوری در برنامه
            self.config['DEFAULT_USERNAME'] = username
            self.config['DEFAULT_AGE'] = age
            self.config['DEFAULT_GENDER'] = gender
            self.config['GLUCOSE_LEVELS']['NORMAL_MIN'] = min_glucose
            self.config['GLUCOSE_LEVELS']['NORMAL_MAX'] = max_glucose

        except ValueError:
            show_message(self.frame, title="خطا", message="لطفاً سن و مقادیر قند خون را به صورت عددی وارد کنید.", message_type="error")
        except Exception as e:
            show_message(self.frame, title="خطا", message=f"خطا در ذخیره تنظیمات کاربر: {e}", message_type="error")
            logging.error(f"خطا در ذخیره تنظیمات کاربر: {e}", exc_info=True)

    def refresh_data(self):
        """بارگذاری مجدد تنظیمات کاربر"""
        self.load_settings()

class ReminderTab(BaseTab):
    """تب یادآوری‌ها"""
    def __init__(self, parent, db_manager, config, colors, fonts):
        self.fonts = fonts # اضافه کردن فونت‌ها
        super().__init__(parent, db_manager, config, colors)
        self.selected_reminder_id = None # برای ویرایش و حذف

    def create_widgets(self):
        """ایجاد ویجت‌های تب یادآوری‌ها"""
        # فریم اصلی محتوا
        content_frame = ttk.Frame(self.frame, style='TFrame')
        content_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # فریم ورودی‌ها برای افزودن/ویرایش یادآوری
        input_frame = ttk.LabelFrame(content_frame, text="افزودن/ویرایش یادآوری", style='TLabelframe')
        input_frame.pack(fill=tk.X, pady=10)

        # ردیف اول: عنوان و تاریخ
        row1_frame = ttk.Frame(input_frame, style='TFrame')
        row1_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(row1_frame, text="عنوان یادآوری:", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.reminder_title_entry = ttk.Entry(row1_frame, font=self.fonts['normal'], style='TEntry', width=30)
        self.reminder_title_entry.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)

        ttk.Label(row1_frame, text="تاریخ:", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.reminder_date_entry = DateEntry(row1_frame, width=12, background=self.colors['accent'], foreground='white', borderwidth=2, date_pattern='yyyy/mm/dd', font=self.fonts['normal'], style='Accent.DateEntry')
        self.reminder_date_entry.pack(side=tk.RIGHT, padx=5)

        # ردیف دوم: زمان و نوع تکرار
        row2_frame = ttk.Frame(input_frame, style='TFrame')
        row2_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(row2_frame, text="زمان (HH:MM):", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.reminder_time_entry = ttk.Entry(row2_frame, font=self.fonts['normal'], style='TEntry', width=8)
        self.reminder_time_entry.pack(side=tk.RIGHT, padx=5)
        self.reminder_time_entry.insert(0, datetime.now().strftime("%H:%M"))

        ttk.Label(row2_frame, text="تکرار:", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.reminder_repeat_var = tk.StringVar(value="Never")
        repeat_options = ["Never", "Daily", "Weekly", "Monthly"]
        self.reminder_repeat_menu = ttk.OptionMenu(row2_frame, self.reminder_repeat_var, self.reminder_repeat_var.get(), *repeat_options, style='TMenubutton')
        self.reminder_repeat_menu.pack(side=tk.RIGHT, padx=5)

        # ردیف سوم: توضیحات
        row3_frame = ttk.Frame(input_frame, style='TFrame')
        row3_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(row3_frame, text="توضیحات (اختیاری):", style='TLabel').pack(side=tk.RIGHT, padx=5)
        self.reminder_notes_entry = ttk.Entry(row3_frame, font=self.fonts['normal'], style='TEntry')
        self.reminder_notes_entry.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)

        # دکمه‌های عملیات
        buttons_frame = ttk.Frame(input_frame, style='TFrame')
        buttons_frame.pack(fill=tk.X, pady=10)
        self.save_reminder_button = ttk.Button(buttons_frame, text="ذخیره یادآوری", command=self.save_reminder, style='Accent.TButton')
        self.save_reminder_button.pack(side=tk.RIGHT, padx=5)
        self.clear_reminder_button = ttk.Button(buttons_frame, text="پاک کردن فرم", command=self.clear_reminder_form, style='TButton')
        self.clear_reminder_button.pack(side=tk.RIGHT, padx=5)

        # فریم نمایش لیست یادآوری‌ها
        list_frame = ttk.LabelFrame(content_frame, text="لیست یادآوری‌ها", style='TLabelframe')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("id", "title", "reminder_time_jalali", "repeat_type", "notes", "is_active")
        self.reminders_tree = ttk.Treeview(list_frame, columns=columns, show="headings", style='Treeview')
        self.reminders_tree.heading("id", text="شناسه")
        self.reminders_tree.heading("title", text="عنوان")
        self.reminders_tree.heading("reminder_time_jalali", text="زمان یادآوری")
        self.reminders_tree.heading("repeat_type", text="تکرار")
        self.reminders_tree.heading("notes", text="توضیحات")
        self.reminders_tree.heading("is_active", text="فعال")

        self.reminders_tree.column("id", width=50, anchor=tk.CENTER)
        self.reminders_tree.column("title", width=200)
        self.reminders_tree.column("reminder_time_jalali", width=150, anchor=tk.CENTER)
        self.reminders_tree.column("repeat_type", width=100, anchor=tk.CENTER)
        self.reminders_tree.column("notes", width=250)
        self.reminders_tree.column("is_active", width=70, anchor=tk.CENTER)

        # اضافه کردن اسکرول بار
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.reminders_tree.yview, style='Vertical.TScrollbar')
        self.reminders_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.reminders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.reminders_tree.bind("<<TreeviewSelect>>", self.on_reminder_select)

        # دکمه‌های مدیریت لیست
        list_buttons_frame = ttk.Frame(list_frame, style='TFrame')
        list_buttons_frame.pack(fill=tk.X, pady=5)
        self.delete_reminder_button = ttk.Button(list_buttons_frame, text="حذف انتخاب شده", command=self.delete_selected_reminder, style='Danger.TButton', state=tk.DISABLED)
        self.delete_reminder_button.pack(side=tk.RIGHT, padx=5)
        self.toggle_active_button = ttk.Button(list_buttons_frame, text="تغییر وضعیت فعال/غیرفعال", command=self.toggle_reminder_active_status, style='TButton', state=tk.DISABLED)
        self.toggle_active_button.pack(side=tk.RIGHT, padx=5)

        self.load_reminders()

    def save_reminder(self):
        """ذخیره یادآوری جدید یا به‌روزرسانی یادآوری موجود"""
        title = self.reminder_title_entry.get().strip()
        date_str = self.reminder_date_entry.get_date().strftime("%Y-%m-%d")
        time_str = self.reminder_time_entry.get().strip()
        repeat_type = self.reminder_repeat_var.get()
        notes = self.reminder_notes_entry.get().strip()

        if not title or not date_str or not time_str:
            show_message(self.frame, title="خطا", message="عنوان، تاریخ و زمان یادآوری نمی‌توانند خالی باشند.", message_type="error")
            return

        try:
            reminder_datetime_str = f"{date_str} {time_str}"
            # اعتبارسنجی فرمت زمان در اینجا انجام نمی‌شود، به دیتابیس واگذار می‌شود یا می‌توان اضافه کرد
            reminder_time = datetime.strptime(reminder_datetime_str, "%Y-%m-%d %H:%M")
        except ValueError:
            show_message(self.frame, title="خطا", message="فرمت تاریخ یا زمان نامعتبر است. لطفاً از فرمت YYYY-MM-DD برای تاریخ و HH:MM برای زمان استفاده کنید.", message_type="error")
            return

        try:
            if self.selected_reminder_id:
                self.db_manager.update_reminder(self.selected_reminder_id, title, reminder_time, repeat_type, notes)
                show_message(self.frame, title="موفقیت", message="یادآوری با موفقیت به‌روزرسانی شد.", message_type="info")
            else:
                self.db_manager.add_reminder(title, reminder_time, repeat_type, notes)
                show_message(self.frame, title="موفقیت", message="یادآوری با موفقیت اضافه شد.", message_type="info")
            
            self.clear_reminder_form()
            self.load_reminders()
        except Exception as e:
            show_message(self.frame, title="خطا", message=f"خطایی در ذخیره یادآوری رخ داد: {e}", message_type="error")
            logging.error(f"خطا در ذخیره یادآوری: {e}", exc_info=True)

    def clear_reminder_form(self):
        """پاک کردن فیلدهای فرم یادآوری"""
        self.reminder_title_entry.delete(0, tk.END)
        self.reminder_date_entry.set_date(datetime.now().date())
        self.reminder_time_entry.delete(0, tk.END)
        self.reminder_time_entry.insert(0, datetime.now().strftime("%H:%M"))
        self.reminder_repeat_var.set("Never")
        self.reminder_notes_entry.delete(0, tk.END)
        self.selected_reminder_id = None
        self.save_reminder_button.config(text="ذخیره یادآوری")
        self.delete_reminder_button.config(state=tk.DISABLED)
        self.toggle_active_button.config(state=tk.DISABLED)
        self.reminders_tree.selection_remove(self.reminders_tree.selection()) # پاک کردن انتخاب از Treeview

    def load_reminders(self):
        """بارگذاری و نمایش لیست یادآوری‌ها از دیتابیس"""
        for item in self.reminders_tree.get_children():
            self.reminders_tree.delete(item)
        
        try:
            reminders = self.db_manager.fetch_all_reminders()
            for reminder in reminders:
                try:
                    reminder_time_jalali = convert_to_jalali(reminder.reminder_time, date_format="%Y-%m-%d %H:%M:%S").strftime("%Y/%m/%d ساعت %H:%M")
                except ValueError:
                     reminder_time_jalali = reminder.reminder_time # اگر تبدیل ناموفق بود
                
                active_status = "فعال" if reminder.is_active else "غیرفعال"
                self.reminders_tree.insert("", tk.END, values=(
                    reminder.id,
                    reminder.title,
                    reminder_time_jalali,
                    reminder.repeat_type,
                    reminder.notes if reminder.notes else "-",
                    active_status
                ))
        except Exception as e:
            show_message(self.frame, title="خطا", message=f"خطایی در بارگذاری یادآوری‌ها رخ داد: {e}", message_type="error")
            logging.error(f"خطا در بارگذاری یادآوری‌ها: {e}", exc_info=True)

    def on_reminder_select(self, event):
        """هنگامی که یک یادآوری از لیست انتخاب می‌شود"""
        selected_items = self.reminders_tree.selection()
        if not selected_items:
            self.clear_reminder_form() # اگر انتخاب برداشته شد، فرم را پاک کن
            return

        selected_item = selected_items[0]
        reminder_values = self.reminders_tree.item(selected_item, "values")
        self.selected_reminder_id = int(reminder_values[0])

        self.reminder_title_entry.delete(0, tk.END)
        self.reminder_title_entry.insert(0, reminder_values[1])
        
        # تبدیل تاریخ جلالی به میلادی برای DateEntry
        try:
            # فرض می‌کنیم فرمت در Treeview به صورت YYYY/MM/DD ساعت HH:MM است
            jalali_datetime_str = reminder_values[2]
            # جدا کردن تاریخ از زمان
            jalali_date_str = jalali_datetime_str.split(' ')[0]
            # تبدیل به میلادی
            gregorian_date = convert_jalali_to_gregorian(jalali_date_str, date_format_jalali="%Y/%m/%d")
            self.reminder_date_entry.set_date(gregorian_date)
            # استخراج زمان
            time_str = jalali_datetime_str.split('ساعت ')[1]
            self.reminder_time_entry.delete(0, tk.END)
            self.reminder_time_entry.insert(0, time_str)
        except Exception as e:
            logging.warning(f"خطا در تبدیل تاریخ/زمان یادآوری برای نمایش در فرم: {e}. مقدار پیش‌فرض استفاده می‌شود.")
            self.reminder_date_entry.set_date(datetime.now().date()) # مقدار پیش‌فرض
            self.reminder_time_entry.delete(0, tk.END)
            self.reminder_time_entry.insert(0, datetime.now().strftime("%H:%M"))

        self.reminder_repeat_var.set(reminder_values[3])
        self.reminder_notes_entry.delete(0, tk.END)
        if reminder_values[4] != "-":
            self.reminder_notes_entry.insert(0, reminder_values[4])
        
        self.save_reminder_button.config(text="به‌روزرسانی یادآوری")
        self.delete_reminder_button.config(state=tk.NORMAL)
        self.toggle_active_button.config(state=tk.NORMAL)

    def delete_selected_reminder(self):
        """حذف یادآوری انتخاب شده از لیست"""
        if not self.selected_reminder_id:
            show_message(self.frame, title="توجه", message="لطفاً ابتدا یک یادآوری را برای حذف انتخاب کنید.", message_type="warning")
            return

        confirm = show_message(self.frame, title="تأیید حذف", message="آیا از حذف این یادآوری مطمئن هستید؟", message_type="question")
        if confirm == 'yes':
            try:
                self.db_manager.delete_reminder(self.selected_reminder_id)
                show_message(self.frame, title="موفقیت", message="یادآوری با موفقیت حذف شد.", message_type="info")
                self.clear_reminder_form()
                self.load_reminders()
            except Exception as e:
                show_message(self.frame, title="خطا", message=f"خطایی در حذف یادآوری رخ داد: {e}", message_type="error")
                logging.error(f"خطا در حذف یادآوری: {e}", exc_info=True)

    def toggle_reminder_active_status(self):
        """تغییر وضعیت فعال/غیرفعال بودن یادآوری انتخاب شده"""
        if not self.selected_reminder_id:
            show_message(self.frame, title="توجه", message="لطفاً ابتدا یک یادآوری را برای تغییر وضعیت انتخاب کنید.", message_type="warning")
            return
        
        try:
            current_status = self.db_manager.get_reminder_status(self.selected_reminder_id)
            if current_status is None:
                show_message(self.frame, title="خطا", message="یادآوری مورد نظر یافت نشد.", message_type="error")
                return
            
            new_status = not current_status
            self.db_manager.update_reminder_status(self.selected_reminder_id, new_status)
            status_text = "فعال" if new_status else "غیرفعال"
            show_message(self.frame, title="موفقیت", message=f"وضعیت یادآوری به '{status_text}' تغییر یافت.", message_type="info")
            self.load_reminders()
            # فرم را پاک نمی‌کنیم تا کاربر بتواند ویرایش‌های دیگر را ادامه دهد یا انتخاب را حفظ کند
            # اما دکمه‌ها را به‌روز می‌کنیم
            selected_items = self.reminders_tree.selection()
            if selected_items: # اگر هنوز آیتمی انتخاب شده است
                self.on_reminder_select(None) # برای بارگذاری مجدد اطلاعات در فرم و به‌روزرسانی دکمه‌ها
            else:
                self.clear_reminder_form()

        except Exception as e:
            show_message(self.frame, title="خطا", message=f"خطایی در تغییر وضعیت یادآوری رخ داد: {e}", message_type="error")
            logging.error(f"خطا در تغییر وضعیت یادآوری: {e}", exc_info=True)

    def refresh_data(self):
        """بارگذاری مجدد داده‌های تب یادآوری‌ها"""
        self.clear_reminder_form()
        self.load_reminders()