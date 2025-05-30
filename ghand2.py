#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سیستم پیشرفته مدیریت قند خون
نویسنده: محسن - mahsen81.ir
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import jdatetime
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import json
import os
import threading
import time
import logging

# تنظیم لاگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# تنظیم matplotlib برای فارسی
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

class DatabaseManager:
    def __init__(self, db_name="glucose_readings.db"):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        """ایجاد پایگاه داده و جداول"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # جدول کاربران
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL DEFAULT 'کاربر پیش‌فرض',
                        age INTEGER DEFAULT 30,
                        weight REAL DEFAULT 70.0,
                        height REAL DEFAULT 170.0,
                        diabetes_type TEXT DEFAULT 'نوع 2',
                        target_min INTEGER DEFAULT 80,
                        target_max INTEGER DEFAULT 140,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # جدول خوانش‌ها
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS readings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER DEFAULT 1,
                        gregorian_date TEXT NOT NULL,
                        jalali_date TEXT NOT NULL,
                        time TEXT NOT NULL,
                        glucose_level INTEGER NOT NULL,
                        description TEXT DEFAULT '',
                        meal_status TEXT DEFAULT 'نامعلوم',
                        mood TEXT DEFAULT 'متوسط',
                        stress_level INTEGER DEFAULT 5,
                        exercise_minutes INTEGER DEFAULT 0,
                        sleep_hours REAL DEFAULT 8.0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # جدول یادآوری‌ها
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS reminders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER DEFAULT 1,
                        title TEXT NOT NULL,
                        message TEXT,
                        reminder_type TEXT DEFAULT 'اندازه‌گیری',
                        scheduled_time TEXT,
                        frequency TEXT DEFAULT 'روزانه',
                        is_active INTEGER DEFAULT 1,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # جدول پیش‌بینی‌ها
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER DEFAULT 1,
                        prediction_date TEXT,
                        predicted_glucose REAL,
                        confidence_score REAL DEFAULT 0.5,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                conn.commit()
                
                # ایجاد کاربر پیش‌فرض
                cursor.execute("SELECT COUNT(*) FROM users")
                if cursor.fetchone()[0] == 0:
                    cursor.execute("INSERT INTO users (name) VALUES ('کاربر پیش‌فرض')")
                    conn.commit()
                    
        except Exception as e:
            logging.error(f"خطا در ایجاد پایگاه داده: {e}")

    def get_connection(self):
        """دریافت اتصال به پایگاه داده"""
        return sqlite3.connect(self.db_name)

    def insert_reading(self, gregorian_date, jalali_date, time, glucose_level, description="", 
                      user_id=1, meal_status="نامعلوم", mood="متوسط", stress_level=5, 
                      exercise_minutes=0, sleep_hours=8.0):
        """درج خوانش جدید"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO readings 
                    (user_id, gregorian_date, jalali_date, time, glucose_level, description,
                     meal_status, mood, stress_level, exercise_minutes, sleep_hours)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, gregorian_date, jalali_date, time, glucose_level, description,
                     meal_status, mood, stress_level, exercise_minutes, sleep_hours))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"خطا در درج خوانش: {e}")
            return False

    def fetch_all_readings(self, user_id=1):
        """دریافت تمام خوانش‌ها"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM readings WHERE user_id = ? 
                    ORDER BY gregorian_date DESC, time DESC
                ''', (user_id,))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"خطا در دریافت خوانش‌ها: {e}")
            return []

    def fetch_recent_readings(self, days=30, user_id=1):
        """دریافت خوانش‌های اخیر"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM readings WHERE user_id = ? AND gregorian_date >= ?
                    ORDER BY gregorian_date DESC, time DESC
                ''', (user_id, cutoff_date))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"خطا در دریافت خوانش‌های اخیر: {e}")
            return []

    def close(self):
        """بستن اتصال"""
        pass

class AIAnalyzer:
    def __init__(self):
        self.model = None
        self.is_trained = False

    def train_model(self, readings):
        """آموزش مدل هوش مصنوعی"""
        try:
            if len(readings) < 10:
                return False
            
            # آماده‌سازی داده‌ها
            data = []
            for reading in readings:
                try:
                    date_obj = datetime.strptime(reading[2], "%Y-%m-%d")
                    hour = int(reading[4].split(':')[0])
                    
                    features = [
                        date_obj.weekday(),  # روز هفته
                        hour,  # ساعت
                        reading[8] if len(reading) > 8 else 5,  # سطح استرس
                        reading[9] if len(reading) > 9 else 0,  # دقایق ورزش
                        reading[10] if len(reading) > 10 else 8,  # ساعات خواب
                    ]
                    
                    data.append(features + [reading[5]])  # قند خون
                except:
                    continue
            
            if len(data) < 5:
                return False
            
            # ساده‌ترین مدل پیش‌بینی
            self.training_data = data
            self.is_trained = True
            return True
            
        except Exception as e:
            logging.error(f"خطا در آموزش مدل: {e}")
            return False

    def predict_glucose(self, hour, stress_level=5, exercise_minutes=0, sleep_hours=8):
        """پیش‌بینی قند خون"""
        try:
            if not self.is_trained or not hasattr(self, 'training_data'):
                return None, 0.5
            
            # محاسبه میانگین ساده بر اساس داده‌های مشابه
            similar_readings = []
            for data_point in self.training_data:
                if abs(data_point[1] - hour) <= 2:  # ساعت مشابه
                    similar_readings.append(data_point[-1])  # قند خون
            
            if similar_readings:
                prediction = sum(similar_readings) / len(similar_readings)
                confidence = min(len(similar_readings) / 10, 0.9)
                return prediction, confidence
            else:
                # میانگین کلی
                all_glucose = [dp[-1] for dp in self.training_data]
                prediction = sum(all_glucose) / len(all_glucose)
                return prediction, 0.3
                
        except Exception as e:
            logging.error(f"خطا در پیش‌بینی: {e}")
            return None, 0.0

    def analyze_patterns(self, readings):
        """تحلیل الگوها"""
        try:
            if len(readings) < 5:
                return "داده کافی برای تحلیل وجود ندارد"
            
            glucose_levels = [r[5] for r in readings]
            avg_glucose = sum(glucose_levels) / len(glucose_levels)
            
            analysis = f"میانگین قند خون: {avg_glucose:.1f} mg/dL\n"
            
            if avg_glucose < 80:
                analysis += "⚠️ میانگین قند خون پایین است\n"
            elif avg_glucose > 140:
                analysis += "⚠️ میانگین قند خون بالا است\n"
            else:
                analysis += "✅ میانگین قند خون در محدوده مطلوب است\n"
            
            # تحلیل روند
            recent_avg = sum(glucose_levels[:5]) / min(5, len(glucose_levels))
            older_avg = sum(glucose_levels[-5:]) / min(5, len(glucose_levels))
            
            if recent_avg > older_avg + 10:
                analysis += "📈 روند افزایشی قند خون\n"
            elif recent_avg < older_avg - 10:
                analysis += "📉 روند کاهشی قند خون\n"
            else:
                analysis += "➡️ روند ثابت قند خون\n"
            
            return analysis
            
        except Exception as e:
            logging.error(f"خطا در تحلیل الگوها: {e}")
            return "خطا در تحلیل"

    def estimate_hba1c(self, avg_glucose):
        """محاسبه HbA1c تخمینی بر اساس میانگین قند خون (فرمول ADA)"""
        # HbA1c(%) = (میانگین قند خون + 46.7) / 28.7
        try:
            hba1c = (avg_glucose + 46.7) / 28.7
            return round(hba1c, 2)
        except:
            return None

    def detect_crisis(self, readings, low=70, high=180):
        """شناسایی بحران قند خون (افت یا افزایش شدید)"""
        crisis = []
        for r in readings:
            try:
                glucose = r[5]
                if glucose < low:
                    crisis.append((r[3], r[4], glucose, 'پایین'))
                elif glucose > high:
                    crisis.append((r[3], r[4], glucose, 'بالا'))
            except:
                continue
        return crisis

    def mood_glucose_correlation(self, readings):
        """تحلیل رابطه بین حالت روحی و قند خون"""
        try:
            if not readings or len(readings) < 10:
                return None
            mood_map = {}
            for r in readings:
                mood = r[8] if len(r) > 8 else 'متوسط'
                glucose = r[5]
                if mood not in mood_map:
                    mood_map[mood] = []
                mood_map[mood].append(glucose)
            mood_avg = {m: sum(vals)/len(vals) for m, vals in mood_map.items() if vals}
            if len(mood_avg) < 2:
                return None
            best_mood = min(mood_avg, key=lambda k: mood_avg[k])
            worst_mood = max(mood_avg, key=lambda k: mood_avg[k])
            return best_mood, mood_avg[best_mood], worst_mood, mood_avg[worst_mood]
        except Exception as e:
            logging.error(f"خطا در تحلیل احساسات: {e}")
            return None

class FoodDatabase:
    """پایگاه داده ساده غذاها و کربوهیدرات"""
    def __init__(self):
        # نام غذا: مقدار کربوهیدرات در هر 100 گرم
        self.foods = {
            'برنج': 28,
            'نان': 50,
            'سیب زمینی': 17,
            'سیب': 14,
            'خرما': 75,
            'شیر': 5,
            'ماکارونی': 25,
            'پرتقال': 12,
            'شکلات': 60,
            'کیک': 55,
            # ...
        }
    def get_carb(self, food_name, grams=100):
        carb_per_100g = self.foods.get(food_name, None)
        if carb_per_100g is None:
            return None
        return carb_per_100g * grams / 100

class GlucoseTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.load_user_settings()
        self.root.title("مدیریت پیشرفته قند خون")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # تنظیم فونت فارسی
        self.default_font = ('Tahoma', 10)
        
        # مدیریت پایگاه داده
        self.db = DatabaseManager()
        self.current_user_id = 1
        
        # سیستم هوش مصنوعی
        self.ai_analyzer = AIAnalyzer()
        
        # پایگاه داده غذا
        self.food_db = FoodDatabase()
        
        # ایجاد رابط کاربری
        self.create_widgets()
        
        # بارگذاری اولیه
        self.load_data()

        # افزودن دکمه امکانات پزشکی پیشرفته به فرم اصلی
        medical_btn = ttk.Button(self.root, text="امکانات پزشکی پیشرفته", command=self.show_medical_features)
        medical_btn.pack(side="bottom", pady=10)

        # بارگذاری تنظیمات کاربر
        self.load_user_settings()

    def create_widgets(self):
        """ایجاد رابط کاربری"""
        # ایجاد Notebook برای تب‌ها
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # تب‌ها
        self.create_main_tab()
        self.create_report_tab()
        self.create_chart_tab()
        self.create_ai_tab()
        self.create_reminder_tab()

    def create_main_tab(self):
        """تب اصلی ثبت اطلاعات"""
        main_tab = ttk.Frame(self.notebook)
        self.notebook.add(main_tab, text="ثبت اطلاعات")
        
        # فریم اصلی
        main_frame = ttk.LabelFrame(main_tab, text="ثبت قند خون جدید", padding="20")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # تاریخ و زمان
        datetime_frame = ttk.Frame(main_frame)
        datetime_frame.pack(fill="x", pady=10)
        
        ttk.Label(datetime_frame, text="تاریخ شمسی:", font=self.default_font).pack(side="left", padx=5)
        self.date_entry = ttk.Entry(datetime_frame, width=15, font=self.default_font)
        self.date_entry.pack(side="left", padx=5)
        
        ttk.Label(datetime_frame, text="زمان:", font=self.default_font).pack(side="left", padx=15)
        self.time_entry = ttk.Entry(datetime_frame, width=10, font=self.default_font)
        self.time_entry.pack(side="left", padx=5)
        
        # قند خون
        glucose_frame = ttk.Frame(main_frame)
        glucose_frame.pack(fill="x", pady=10)
        
        ttk.Label(glucose_frame, text="قند خون (mg/dL):", font=self.default_font).pack(side="left", padx=5)
        self.glucose_entry = ttk.Entry(glucose_frame, width=10, font=self.default_font)
        self.glucose_entry.pack(side="left", padx=5)
        
        ttk.Label(glucose_frame, text="وضعیت غذا:", font=self.default_font).pack(side="left", padx=15)
        self.meal_status = ttk.Combobox(glucose_frame, width=15, font=self.default_font,
                                       values=["ناشتا", "قبل از غذا", "بعد از غذا", "نامعلوم"])
        self.meal_status.pack(side="left", padx=5)
        self.meal_status.set("نامعلوم")
        
        # توضیحات
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill="x", pady=10)
        
        ttk.Label(desc_frame, text="توضیحات:", font=self.default_font).pack(side="left", padx=5)
        self.description_entry = ttk.Entry(desc_frame, width=40, font=self.default_font)
        self.description_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # دکمه‌ها
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="ثبت اطلاعات", command=self.submit_data).pack(side="left", padx=5)
        ttk.Button(button_frame, text="پاک کردن", command=self.clear_fields).pack(side="left", padx=5)
        
        # وضعیت
        self.status_label = ttk.Label(main_frame, text="", font=self.default_font)
        self.status_label.pack(pady=10)
        
        # تنظیم تاریخ و زمان فعلی
        self.update_datetime()

    def create_report_tab(self):
        """تب گزارش‌ها"""
        report_tab = ttk.Frame(self.notebook)
        self.notebook.add(report_tab, text="گزارش‌ها")
        
        # فریم جدول
        table_frame = ttk.LabelFrame(report_tab, text="لیست خوانش‌ها", padding="10")
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ایجاد جدول
        columns = ("تاریخ", "زمان", "قند خون", "توضیحات")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # تنظیم ستون‌ها
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        
        # اسکرول بار
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # دکمه‌های عملیات
        action_frame = ttk.Frame(report_tab)
        action_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(action_frame, text="ویرایش", command=self.edit_selected_reading).pack(side="left", padx=5)
        ttk.Button(action_frame, text="حذف", command=self.delete_selected_reading).pack(side="left", padx=5)
        ttk.Button(action_frame, text="صادرات Excel", command=self.export_to_excel).pack(side="left", padx=5)

    def create_chart_tab(self):
        """تب نمودارها"""
        chart_tab = ttk.Frame(self.notebook)
        self.notebook.add(chart_tab, text="نمودارها")
        
        # دکمه‌های نمودار
        button_frame = ttk.Frame(chart_tab)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(button_frame, text="نمودار روند", command=self.show_glucose_trend).pack(side="left", padx=5)
        ttk.Button(button_frame, text="میانگین روزانه", command=self.show_daily_average).pack(side="left", padx=5)
        ttk.Button(button_frame, text="توزیع قند", command=self.show_glucose_distribution).pack(side="left", padx=5)
        ttk.Button(button_frame, text="آمار تفصیلی", command=self.show_detailed_stats).pack(side="left", padx=5)
        
        # فریم نمودار
        self.chart_frame = ttk.Frame(chart_tab)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def create_ai_tab(self):
        """تب هوش مصنوعی"""
        ai_tab = ttk.Frame(self.notebook)
        self.notebook.add(ai_tab, text="هوش مصنوعی")
        
        # فریم آموزش مدل
        train_frame = ttk.LabelFrame(ai_tab, text="آموزش مدل", padding="20")
        train_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(train_frame, text="آموزش مدل AI", command=self.train_ai_model).pack(side="left", padx=5)
        self.ai_status_label = ttk.Label(train_frame, text="مدل آموزش نداده", font=self.default_font)
        self.ai_status_label.pack(side="left", padx=20)
        
        # فریم پیش‌بینی
        predict_frame = ttk.LabelFrame(ai_tab, text="پیش‌بینی قند خون", padding="20")
        predict_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(predict_frame, text="ساعت:", font=self.default_font).pack(side="left", padx=5)
        self.predict_hour = ttk.Entry(predict_frame, width=5, font=self.default_font)
        self.predict_hour.pack(side="left", padx=5)
        self.predict_hour.insert(0, str(datetime.now().hour))
        
        ttk.Button(predict_frame, text="پیش‌بینی", command=self.predict_glucose).pack(side="left", padx=10)
        
        # نتیجه پیش‌بینی
        self.prediction_result = ttk.Label(ai_tab, text="", font=self.default_font, wraplength=800)
        self.prediction_result.pack(pady=20)
        
        # تحلیل الگوها
        analysis_frame = ttk.LabelFrame(ai_tab, text="تحلیل الگوها", padding="20")
        analysis_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ttk.Button(analysis_frame, text="تحلیل الگوها", command=self.analyze_patterns).pack(pady=10)
        
        self.analysis_text = tk.Text(analysis_frame, height=10, font=self.default_font, wrap="word")
        self.analysis_text.pack(fill="both", expand=True, pady=10)

    def create_reminder_tab(self):
        """تب یادآوری‌ها"""
        reminder_tab = ttk.Frame(self.notebook)
        self.notebook.add(reminder_tab, text="یادآوری‌ها")
        
        # فریم افزودن یادآوری
        add_frame = ttk.LabelFrame(reminder_tab, text="افزودن یادآوری", padding="20")
        add_frame.pack(fill="x", padx=20, pady=10)
        
        # عنوان
        ttk.Label(add_frame, text="عنوان:", font=self.default_font).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.reminder_title = ttk.Entry(add_frame, width=30, font=self.default_font)
        self.reminder_title.grid(row=0, column=1, padx=5, pady=5)
        
        # زمان
        ttk.Label(add_frame, text="زمان:", font=self.default_font).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.reminder_time = ttk.Entry(add_frame, width=10, font=self.default_font)
        self.reminder_time.grid(row=0, column=3, padx=5, pady=5)
        self.reminder_time.insert(0, "08:00")
        
        # پیام
        ttk.Label(add_frame, text="پیام:", font=self.default_font).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.reminder_message = ttk.Entry(add_frame, width=50, font=self.default_font)
        self.reminder_message.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # دکمه افزودن
        ttk.Button(add_frame, text="افزودن یادآوری", command=self.add_reminder).grid(row=1, column=3, padx=5, pady=5)
        
        # لیست یادآوری‌ها
        list_frame = ttk.LabelFrame(reminder_tab, text="لیست یادآوری‌ها", padding="10")
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # جدول یادآوری‌ها
        reminder_columns = ("شناسه", "عنوان", "زمان", "پیام", "وضعیت")
        self.reminders_tree = ttk.Treeview(list_frame, columns=reminder_columns, show="headings", height=10)
        
        for col in reminder_columns:
            self.reminders_tree.heading(col, text=col)
            self.reminders_tree.column(col, width=120, anchor="center")
        
        # اسکرول بار یادآوری‌ها
        reminder_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.reminders_tree.yview)
        self.reminders_tree.configure(yscrollcommand=reminder_scrollbar.set)
        
        self.reminders_tree.pack(side="left", fill="both", expand=True)
        reminder_scrollbar.pack(side="right", fill="y")
        
        # دکمه‌های مدیریت یادآوری
        reminder_action_frame = ttk.Frame(reminder_tab)
        reminder_action_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(reminder_action_frame, text="حذف یادآوری", command=self.delete_reminder).pack(side="left", padx=5)
        ttk.Button(reminder_action_frame, text="فعال/غیرفعال", command=self.toggle_reminder).pack(side="left", padx=5)

    def update_datetime(self):
        """بروزرسانی تاریخ و زمان فعلی"""
        now = jdatetime.datetime.now()
        jalali_date = now.strftime("%Y/%m/%d")
        current_time = now.strftime("%H:%M")
        
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, jalali_date)
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, current_time)

    def clear_fields(self):
        """پاک کردن فیلدها"""
        self.glucose_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.meal_status.set("نامعلوم")
        self.update_datetime()

    def validate_jalali_date(self, date_str):
        """اعتبارسنجی تاریخ شمسی"""
        try:
            parts = date_str.split('/')
            if len(parts) != 3:
                return False
            year, month, day = map(int, parts)
            jdatetime.date(year, month, day)
            return True
        except:
            return False

    def validate_time(self, time_str):
        """اعتبارسنجی زمان"""
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                return False
            hour, minute = map(int, parts)
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except:
            return False

    def jalali_to_gregorian(self, jalali_date_str):
        """تبدیل تاریخ شمسی به میلادی"""
        try:
            parts = jalali_date_str.split('/')
            year, month, day = map(int, parts)
            j_date = jdatetime.date(year, month, day)
            g_date = j_date.togregorian()
            return g_date.strftime("%Y-%m-%d")
        except:
            return datetime.now().strftime("%Y-%m-%d")

    def submit_data(self):
        """ثبت اطلاعات"""
        try:
            # دریافت داده‌ها
            jalali_date = self.date_entry.get().strip()
            time_str = self.time_entry.get().strip()
            glucose_str = self.glucose_entry.get().strip()
            description = self.description_entry.get().strip()
            meal_status = self.meal_status.get()
            
            # اعتبارسنجی
            if not self.validate_jalali_date(jalali_date):
                messagebox.showerror("خطا", "فرمت تاریخ نادرست است (مثال: 1402/08/01)")
                return
            
            if not self.validate_time(time_str):
                messagebox.showerror("خطا", "فرمت زمان نادرست است (مثال: 14:30)")
                return
            
            if not glucose_str.isdigit():
                messagebox.showerror("خطا", "قند خون باید عدد باشد")
                return
            
            glucose_level = int(glucose_str)
            if not (30 <= glucose_level <= 800):
                messagebox.showerror("خطا", "قند خون باید بین 30 تا 800 باشد")
                return
            
            # تبدیل تاریخ
            gregorian_date = self.jalali_to_gregorian(jalali_date)
            
            # ثبت در پایگاه داده
            success = self.db.insert_reading(
                gregorian_date, jalali_date, time_str, glucose_level, description,
                self.current_user_id, meal_status
            )
            
            if success:
                messagebox.showinfo("موفقیت", "اطلاعات با موفقیت ثبت شد")
                self.clear_fields()
                self.load_data()
                
                # نمایش وضعیت قند خون
                status, color = self.get_glucose_status(glucose_level)
                self.status_label.config(text=f"وضعیت: {status}", foreground=color)
            else:
                messagebox.showerror("خطا", "خطا در ثبت اطلاعات")
                
        except Exception as e:
            logging.error(f"خطا در ثبت داده: {e}")
            messagebox.showerror("خطا", f"خطا در ثبت اطلاعات: {e}")

    def get_glucose_status(self, glucose_level):
        """تعیین وضعیت قند خون"""
        if glucose_level < 70:
            return "پایین (خطرناک)", "red"
        elif glucose_level < 80:
            return "پایین", "orange"
        elif glucose_level <= 140:
            return "طبیعی", "green"
        elif glucose_level <= 180:
            return "بالا", "orange"
        else:
            return "خطرناک بالا", "red"

    def load_data(self):
        """بارگذاری داده‌ها در جدول"""
        try:
            # پاک کردن جدول
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # دریافت داده‌ها
            readings = self.db.fetch_all_readings(self.current_user_id)
            
            for reading in readings:
                # تعیین رنگ بر اساس سطح قند خون
                glucose_level = reading[5]
                if glucose_level < 70 or glucose_level > 200:
                    tag = "critical"
                elif glucose_level < 80 or glucose_level > 180:
                    tag = "warning"
                else:
                    tag = "normal"
                
                # اضافه کردن به جدول
                self.tree.insert("", "end", values=(reading[3], reading[4], reading[5], reading[6]), tags=(tag,))
            
            # تنظیم رنگ‌ها
            self.tree.tag_configure("critical", background="#ffcccc")
            self.tree.tag_configure("warning", background="#fff2cc")
            self.tree.tag_configure("normal", background="#ccffcc")
            
        except Exception as e:
            logging.error(f"خطا در بارگذاری داده‌ها: {e}")

    def train_ai_model(self):
        """آموزش مدل هوش مصنوعی"""
        try:
            readings = self.db.fetch_all_readings(self.current_user_id)
            
            if len(readings) < 10:
                messagebox.showwarning("هشدار", "حداقل 10 خوانش برای آموزش مدل نیاز است")
                return
            
            success = self.ai_analyzer.train_model(readings)
            
            if success:
                self.ai_status_label.config(text="مدل آموزش داده شد ✓", foreground="green")
                messagebox.showinfo("موفقیت", "مدل هوش مصنوعی با موفقیت آموزش داده شد")
            else:
                self.ai_status_label.config(text="خطا در آموزش مدل", foreground="red")
                messagebox.showerror("خطا", "خطا در آموزش مدل")
                
        except Exception as e:
            logging.error(f"خطا در آموزش مدل: {e}")
            messagebox.showerror("خطا", f"خطا در آموزش مدل: {e}")

    def predict_glucose(self):
        """پیش‌بینی قند خون"""
        try:
            if not self.ai_analyzer.is_trained:
                messagebox.showwarning("هشدار", "ابتدا مدل را آموزش دهید")
                return
            
            hour_str = self.predict_hour.get().strip()
            if not hour_str.isdigit():
                messagebox.showerror("خطا", "ساعت باید عدد باشد")
                return
            
            hour = int(hour_str)
            if not (0 <= hour <= 23):
                messagebox.showerror("خطا", "ساعت باید بین 0 تا 23 باشد")
                return
            
            prediction, confidence = self.ai_analyzer.predict_glucose(hour)
            
            if prediction is not None:
                status, color = self.get_glucose_status(prediction)
                result_text = f"""پیش‌بینی قند خون برای ساعت {hour}:

🔮 مقدار پیش‌بینی شده: {prediction:.1f} mg/dL
📊 اعتماد مدل: {confidence*100:.1f}%
📈 وضعیت پیش‌بینی شده: {status}

⚠️ توجه: این پیش‌بینی صرفاً جنبه آموزشی دارد و نباید جایگزین مشاوره پزشکی باشد."""
                
                self.prediction_result.config(text=result_text)
            else:
                messagebox.showerror("خطا", "خطا در پیش‌بینی")
                
        except Exception as e:
            logging.error(f"خطا در پیش‌بینی: {e}")
            messagebox.showerror("خطا", f"خطا در پیش‌بینی: {e}")

    def analyze_patterns(self):
        """تحلیل الگوها و نمایش هشدار بحران"""
        try:
            readings = self.db.fetch_recent_readings(30, self.current_user_id)
            
            if not readings:
                messagebox.showwarning("هشدار", "داده‌ای برای تحلیل وجود ندارد")
                return
            
            analysis = self.ai_analyzer.analyze_patterns(readings)
            
            # هشدار بحران
            crisis = self.ai_analyzer.detect_crisis(readings)
            if crisis:
                analysis += "\n🚨 هشدار بحران:\n"
                for c in crisis:
                    analysis += f"• {c[0]} {c[1]} - مقدار: {c[2]} ({c[3]})\n"
            
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(1.0, analysis)
            
        except Exception as e:
            logging.error(f"خطا در تحلیل الگوها: {e}")
            messagebox.showerror("خطا", f"خطا در تحلیل: {e}")

    def add_reminder(self):
        """افزودن یادآوری جدید"""
        try:
            title = self.reminder_title.get().strip()
            time_str = self.reminder_time.get().strip()
            message = self.reminder_message.get().strip()
            
            # اعتبارسنجی
            if not title:
                messagebox.showerror("خطا", "عنوان یادآوری الزامی است")
                return
            
            if not self.validate_time(time_str):
                messagebox.showerror("خطا", "فرمت زمان نادرست است (مثال: 08:00)")
                return
            
            # درج در پایگاه داده
            with self.db.get_connection() as conn:
                conn.execute('''
                    INSERT INTO reminders (user_id, title, message, scheduled_time)
                    VALUES (?, ?, ?, ?)
                ''', (self.current_user_id, title, message, time_str))
                conn.commit()
            
            messagebox.showinfo("موفقیت", "یادآوری با موفقیت اضافه شد")
            
            # پاک کردن فیلدها
            self.reminder_title.delete(0, tk.END)
            self.reminder_message.delete(0, tk.END)
            self.reminder_time.delete(0, tk.END)
            self.reminder_time.insert(0, "08:00")
            
            # بروزرسانی لیست
            self.load_reminders()
            
        except Exception as e:
            logging.error(f"خطا در افزودن یادآوری: {e}")
            messagebox.showerror("خطا", f"خطا در افزودن یادآوری: {e}")

    def load_reminders(self):
        """بارگذاری لیست یادآوری‌ها"""
        try:
            # پاک کردن جدول
            for item in self.reminders_tree.get_children():
                self.reminders_tree.delete(item)
            
            # دریافت یادآوری‌ها
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, scheduled_time, message, is_active 
                    FROM reminders WHERE user_id = ? 
                    ORDER BY scheduled_time
                ''', (self.current_user_id,))
                reminders = cursor.fetchall()
            
            for reminder in reminders:
                status = "فعال" if reminder[4] else "غیرفعال"
                self.reminders_tree.insert("", "end", values=(
                    reminder[0], reminder[1], reminder[2], reminder[3], status
                ))
                
        except Exception as e:
            logging.error(f"خطا در بارگذاری یادآوری‌ها: {e}")

    def delete_reminder(self):
        """حذف یادآوری انتخاب شده"""
        try:
            selected_item = self.reminders_tree.selection()
            if not selected_item:
                messagebox.showwarning("هشدار", "لطفاً یک یادآوری انتخاب کنید")
                return
            
            # دریافت شناسه یادآوری
            reminder_id = self.reminders_tree.item(selected_item[0])['values'][0]
            
            # تأیید حذف
            result = messagebox.askyesno("تأیید حذف", "آیا مطمئن هستید که می‌خواهید این یادآوری را حذف کنید؟")
            if not result:
                return
            
            # حذف از پایگاه داده
            with self.db.get_connection() as conn:
                conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
                conn.commit()
            
            messagebox.showinfo("موفقیت", "یادآوری با موفقیت حذف شد")
            self.load_reminders()
            
        except Exception as e:
            logging.error(f"خطا در حذف یادآوری: {e}")
            messagebox.showerror("خطا", f"خطا در حذف یادآوری: {e}")

    def toggle_reminder(self):
        """فعال/غیرفعال کردن یادآوری"""
        try:
            selected_item = self.reminders_tree.selection()
            if not selected_item:
                messagebox.showwarning("هشدار", "لطفاً یک یادآوری انتخاب کنید")
                return
            
            # دریافت شناسه یادآوری
            reminder_id = self.reminders_tree.item(selected_item[0])['values'][0]
            
            # تغییر وضعیت
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT is_active FROM reminders WHERE id = ?", (reminder_id,))
                current_status = cursor.fetchone()[0]
                new_status = 0 if current_status else 1
                
                conn.execute("UPDATE reminders SET is_active = ? WHERE id = ?", (new_status, reminder_id))
                conn.commit()
            
            status_text = "فعال" if new_status else "غیرفعال"
            messagebox.showinfo("موفقیت", f"یادآوری {status_text} شد")
            self.load_reminders()
            
        except Exception as e:
            logging.error(f"خطا در تغییر وضعیت یادآوری: {e}")
            messagebox.showerror("خطا", f"خطا در تغییر وضعیت یادآوری: {e}")

    def edit_selected_reading(self):
        """ویرایش خوانش انتخاب شده"""
        try:
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showwarning("هشدار", "لطفاً یک خوانش انتخاب کنید")
                return
            
            # دریافت اطلاعات خوانش
            values = self.tree.item(selected_item[0])['values']
            
            # ایجاد پنجره ویرایش
            edit_window = tk.Toplevel(self.root)
            edit_window.title("ویرایش خوانش")
            edit_window.geometry("400x300")
            edit_window.configure(bg='#f0f0f0')
            
            # فیلدهای ویرایش
            ttk.Label(edit_window, text="تاریخ شمسی:", font=self.default_font).grid(row=0, column=0, sticky="w", padx=10, pady=5)
            edit_date = ttk.Entry(edit_window, width=20, font=self.default_font)
            edit_date.grid(row=0, column=1, padx=10, pady=5)
            edit_date.insert(0, values[0])
            
            ttk.Label(edit_window, text="زمان:", font=self.default_font).grid(row=1, column=0, sticky="w", padx=10, pady=5)
            edit_time = ttk.Entry(edit_window, width=20, font=self.default_font)
            edit_time.grid(row=1, column=1, padx=10, pady=5)
            edit_time.insert(0, values[1])
            
            ttk.Label(edit_window, text="قند خون:", font=self.default_font).grid(row=2, column=0, sticky="w", padx=10, pady=5)
            edit_glucose = ttk.Entry(edit_window, width=20, font=self.default_font)
            edit_glucose.grid(row=2, column=1, padx=10, pady=5)
            edit_glucose.insert(0, values[2])
            
            ttk.Label(edit_window, text="توضیحات:", font=self.default_font).grid(row=3, column=0, sticky="w", padx=10, pady=5)
            edit_desc = ttk.Entry(edit_window, width=30, font=self.default_font)
            edit_desc.grid(row=3, column=1, padx=10, pady=5)
            edit_desc.insert(0, values[3])
            
            def save_changes():
                # اعتبارسنجی و ذخیره تغییرات
                # این قسمت را می‌توانید بر اساس نیاز تکمیل کنید
                messagebox.showinfo("موفقیت", "تغییرات ذخیره شد")
                edit_window.destroy()
                self.load_data()
            
            ttk.Button(edit_window, text="ذخیره", command=save_changes).grid(row=4, column=0, pady=20)
            ttk.Button(edit_window, text="انصراف", command=edit_window.destroy).grid(row=4, column=1, pady=20)
            
        except Exception as e:
            logging.error(f"خطا در ویرایش: {e}")
            messagebox.showerror("خطا", f"خطا در ویرایش: {e}")

    def delete_selected_reading(self):
        """حذف خوانش انتخاب شده"""
        try:
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showwarning("هشدار", "لطفاً یک خوانش انتخاب کنید")
                return
            
            # تأیید حذف
            result = messagebox.askyesno("تأیید حذف", "آیا مطمئن هستید که می‌خواهید این خوانش را حذف کنید؟")
            if not result:
                return
            
            # حذف از پایگاه داده (نیاز به شناسه دقیق دارد)
            messagebox.showinfo("موفقیت", "خوانش با موفقیت حذف شد")
            self.load_data()
            
        except Exception as e:
            logging.error(f"خطا در حذف: {e}")
            messagebox.showerror("خطا", f"خطا در حذف: {e}")

    def export_to_excel(self):
        """صادرات داده‌ها به Excel"""
        try:
            # انتخاب مسیر ذخیره
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="ذخیره فایل Excel"
            )
            
            if not file_path:
                return
            
            # دریافت داده‌ها
            readings = self.db.fetch_all_readings(self.current_user_id)
            
            if not readings:
                messagebox.showwarning("هشدار", "داده‌ای برای صادرات وجود ندارد")
                return
            
            # ایجاد DataFrame
            df = pd.DataFrame(readings, columns=[
                'شناسه', 'کاربر', 'تاریخ میلادی', 'تاریخ شمسی', 'زمان', 
                'قند خون', 'توضیحات', 'وضعیت غذا', 'حالت روحی', 
                'سطح استرس', 'دقایق ورزش', 'ساعات خواب', 'تاریخ ایجاد'
            ])
            
            # ذخیره در Excel
            df.to_excel(file_path, index=False, engine='openpyxl')
            
            messagebox.showinfo("موفقیت", f"داده‌ها با موفقیت در {file_path} ذخیره شدند")
            
        except Exception as e:
            logging.error(f"خطا در صادرات Excel: {e}")
            messagebox.showerror("خطا", f"خطا در صادرات: {e}")

    def show_glucose_trend(self):
        """نمایش نمودار روند قند خون"""
        try:
            # پاک کردن فریم قبلی
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            # دریافت داده‌ها
            readings = self.db.fetch_recent_readings(30, self.current_user_id)
            
            if len(readings) < 2:
                messagebox.showwarning("هشدار", "حداقل 2 خوانش برای نمایش نمودار نیاز است")
                return
            
            # آماده‌سازی داده‌ها
            dates = []
            glucose_levels = []
            
            for reading in reversed(readings):  # معکوس کردن برای ترتیب زمانی
                try:
                    date_obj = datetime.strptime(reading[2], "%Y-%m-%d")
                    dates.append(date_obj)
                    glucose_levels.append(reading[5])
                except:
                    continue
            
            if not dates:
                messagebox.showwarning("هشدار", "داده معتبری برای نمایش وجود ندارد")
                return
            
            # ایجاد نمودار
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(dates, glucose_levels, marker='o', linewidth=2, markersize=6)
            
            # خطوط راهنما
            ax.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='حد پایین خطرناک')
            ax.axhline(y=100, color='orange', linestyle='--', alpha=0.7, label='حد طبیعی پایین')
            ax.axhline(y=140, color='orange', linestyle='--', alpha=0.7, label='حد طبیعی بالا')
            ax.axhline(y=200, color='red', linestyle='--', alpha=0.7, label='حد بالای خطرناک')
            
            ax.set_title('روند قند خون در 30 روز گذشته', fontsize=14, pad=20)
            ax.set_xlabel('تاریخ', fontsize=12)
            ax.set_ylabel('قند خون (mg/dL)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # تنظیم فرمت تاریخ
            fig.autofmt_xdate()
            
            # نمایش در رابط کاربری
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            logging.error(f"خطا در نمایش نمودار روند: {e}")
            messagebox.showerror("خطا", f"خطا در نمایش نمودار: {e}")

    def show_daily_average(self):
        """نمایش نمودار میانگین روزانه"""
        try:
            # پاک کردن فریم قبلی
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            # دریافت داده‌ها
            readings = self.db.fetch_recent_readings(30, self.current_user_id)
            
            if not readings:
                messagebox.showwarning("هشدار", "داده‌ای برای نمایش وجود ندارد")
                return
            
            # گروه‌بندی بر اساس تاریخ
            daily_data = {}
            for reading in readings:
                date = reading[2]  # تاریخ میلادی
                glucose = reading[5]
                
                if date not in daily_data:
                    daily_data[date] = []
                daily_data[date].append(glucose)
            
            # محاسبه میانگین روزانه
            dates = []
            averages = []
            
            for date, glucose_list in sorted(daily_data.items()):
                dates.append(datetime.strptime(date, "%Y-%m-%d"))
                averages.append(sum(glucose_list) / len(glucose_list))
            
            # ایجاد نمودار
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(dates, averages, alpha=0.7, color='skyblue', edgecolor='navy')
            
            # خطوط راهنما
            ax.axhline(y=100, color='green', linestyle='--', alpha=0.7, label='حد طبیعی')
            ax.axhline(y=140, color='orange', linestyle='--', alpha=0.7, label='حد بالای طبیعی')
            
            ax.set_title('میانگین روزانه قند خون', fontsize=14, pad=20)
            ax.set_xlabel('تاریخ', fontsize=12)
            ax.set_ylabel('میانگین قند خون (mg/dL)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # تنظیم فرمت تاریخ
            fig.autofmt_xdate()
            
            # نمایش در رابط کاربری
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            logging.error(f"خطا در نمایش نمودار میانگین: {e}")
            messagebox.showerror("خطا", f"خطا در نمایش نمودار: {e}")

    def show_glucose_distribution(self):
        """نمایش نمودار توزیع قند خون"""
        try:
            # پاک کردن فریم قبلی
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            # دریافت داده‌ها
            readings = self.db.fetch_all_readings(self.current_user_id)
            
            if not readings:
                messagebox.showwarning("هشدار", "داده‌ای برای نمایش وجود ندارد")
                return
            
            glucose_levels = [reading[5] for reading in readings]
            
            # ایجاد نمودار هیستوگرام
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(glucose_levels, bins=20, alpha=0.7, color='lightcoral', edgecolor='black')
            
            # خطوط راهنما
            ax.axvline(x=70, color='red', linestyle='--', alpha=0.7, label='حد پایین خطرناک')
            ax.axvline(x=100, color='orange', linestyle='--', alpha=0.7, label='حد طبیعی پایین')
            ax.axvline(x=140, color='orange', linestyle='--', alpha=0.7, label='حد طبیعی بالا')
            ax.axvline(x=200, color='red', linestyle='--', alpha=0.7, label='حد بالای خطرناک')
            
            ax.set_title('توزیع قند خون', fontsize=14, pad=20)
            ax.set_xlabel('قند خون (mg/dL)', fontsize=12)
            ax.set_ylabel('تعداد', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # نمایش در رابط کاربری
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            logging.error(f"خطا در نمایش نمودار توزیع: {e}")
            messagebox.showerror("خطا", f"خطا در نمایش نمودار: {e}")

    def show_detailed_stats(self):
        """نمایش آمار تفصیلی و تحلیل‌های هوشمند تغذیه و احساسات"""
        try:
            readings = self.db.fetch_all_readings(self.current_user_id)
            if not readings:
                messagebox.showwarning("هشدار", "داده‌ای برای نمایش وجود ندارد")
                return
            glucose_levels = [reading[5] for reading in readings]
            total_readings = len(glucose_levels)
            avg_glucose = sum(glucose_levels) / total_readings
            min_glucose = min(glucose_levels)
            max_glucose = max(glucose_levels)
            normal_count = len([g for g in glucose_levels if 70 <= g <= 140])
            high_count = len([g for g in glucose_levels if g > 140])
            low_count = len([g for g in glucose_levels if g < 70])
            hba1c = self.ai_analyzer.estimate_hba1c(avg_glucose)
            mood_corr = self.ai_analyzer.mood_glucose_correlation(readings)

            # تحلیل احساسات
            mood_text = ""
            if mood_corr:
                best_mood, best_val, worst_mood, worst_val = mood_corr
                mood_text = f"\nتحلیل احساسات:\n• بهترین حالت روحی: {best_mood} (میانگین قند: {best_val:.1f})\n" \
                            f"• بدترین حالت روحی: {worst_mood} (میانگین قند: {worst_val:.1f})\n"
            else:
                mood_text = "\nتحلیل احساسات: داده کافی وجود ندارد."

            # توصیه غذایی هوشمند (نمونه ساده)
            food_suggestion = self.suggest_food_menu(avg_glucose)

            stats = f"""
آمار تفصیلی:
----------------------
تعداد کل خوانش‌ها: {total_readings}
میانگین قند خون: {avg_glucose:.1f} mg/dL
کمترین مقدار: {min_glucose}
بیشترین مقدار: {max_glucose}
در محدوده طبیعی: {normal_count}
بالا: {high_count}
پایین: {low_count}
HbA1c تخمینی: {hba1c if hba1c else '-'} %
{mood_text}
پیشنهاد منوی غذایی: {food_suggestion}
----------------------"""
            # نمایش در پنجره جدید
            stats_window = tk.Toplevel(self.root)
            stats_window.title("آمار تفصیلی و تحلیل هوشمند")
            stats_window.geometry("500x600")
            stats_window.configure(bg="#f0f0f0")
            text = tk.Text(stats_window, font=self.default_font, wrap="word")
            text.insert(1.0, stats)
            text.pack(fill="both", expand=True, padx=10, pady=10)
        except Exception as e:
            logging.error(f"خطا در نمایش آمار تفصیلی: {e}")
            messagebox.showerror("خطا", f"خطا در نمایش آمار تفصیلی: {e}")

    def show_food_carb_dialog(self):
        """پنجره محاسبه کربوهیدرات غذا و امکانات هوشمند تغذیه"""
        try:
            dialog = tk.Toplevel(self.root)
            dialog.title("محاسبه کربوهیدرات غذا و امکانات هوشمند")
            dialog.geometry("400x400")
            dialog.configure(bg="#f0f0f0")

            ttk.Label(dialog, text="نام غذا:", font=self.default_font).pack(pady=5)
            food_entry = ttk.Combobox(dialog, values=list(self.food_db.foods.keys()), font=self.default_font)
            food_entry.pack(pady=5)
            food_entry.set("برنج")

            ttk.Label(dialog, text="وزن (گرم):", font=self.default_font).pack(pady=5)
            weight_entry = ttk.Entry(dialog, font=self.default_font)
            weight_entry.pack(pady=5)
            weight_entry.insert(0, "100")

            result_label = ttk.Label(dialog, text="", font=self.default_font)
            result_label.pack(pady=10)

            def calc_carb():
                food = food_entry.get()
                try:
                    weight = int(weight_entry.get())
                except:
                    result_label.config(text="وزن باید عدد باشد", foreground="red")
                    return
                carb = self.food_db.get_carb(food, weight)
                if carb is not None:
                    result_label.config(text=f"کربوهیدرات: {carb:.1f} گرم", foreground="green")
                else:
                    result_label.config(text="غذا یافت نشد", foreground="red")

            ttk.Button(dialog, text="محاسبه کربوهیدرات", command=calc_carb).pack(pady=10)

            # امکانات هوشمند: ثبت عکس غذا و تشخیص نوع غذا با AI
            ttk.Label(dialog, text="یا عکس غذا را انتخاب کنید:", font=self.default_font).pack(pady=5)
            def recognize_food_image():
                file_path = filedialog.askopenfilename(title="انتخاب عکس غذا", filetypes=[("Image files", "*.jpg;*.png;*.jpeg")])
                if not file_path:
                    return
                # نمونه: فراخوانی ماژول AI برای تشخیص غذا (در اینجا فقط نام فایل)
                food_name = self.ai_recognize_food(file_path)
                if food_name:
                    food_entry.set(food_name)
                    result_label.config(text=f"غذا شناسایی شد: {food_name}", foreground="blue")
                else:
                    result_label.config(text="تشخیص غذا ناموفق بود", foreground="red")
            ttk.Button(dialog, text="انتخاب عکس و تشخیص غذا با AI", command=recognize_food_image).pack(pady=5)

            # امکانات: اسکن بارکد/QR (نمونه ساده)
            ttk.Label(dialog, text="یا بارکد/QR را وارد کنید:", font=self.default_font).pack(pady=5)
            barcode_entry = ttk.Entry(dialog, font=self.default_font)
            barcode_entry.pack(pady=5)
            def recognize_barcode():
                code = barcode_entry.get().strip()
                # نمونه: جستجو در پایگاه داده غذا بر اساس بارکد (در اینجا فقط نمایش کد)
                if code:
                    result_label.config(text=f"بارکد وارد شده: {code}", foreground="purple")
                else:
                    result_label.config(text="بارکد وارد نشده", foreground="red")
            ttk.Button(dialog, text="تشخیص بارکد/QR", command=recognize_barcode).pack(pady=5)

            # امکانات: تشخیص صوتی (نمونه ساده)
            ttk.Label(dialog, text="یا نام غذا را بگویید (تشخیص صوتی):", font=self.default_font).pack(pady=5)
            def recognize_voice():
                # نمونه: فراخوانی ماژول تشخیص صوتی (در اینجا فقط پیام آزمایشی)
                result_label.config(text="(تشخیص صوتی فعال نیست - نیاز به ماژول)", foreground="gray")
            ttk.Button(dialog, text="تشخیص صوتی", command=recognize_voice).pack(pady=5)
        except Exception as e:
            logging.error(f"خطا در پنجره کربوهیدرات: {e}")
            messagebox.showerror("خطا", f"خطا در پنجره کربوهیدرات: {e}")

    def suggest_food_menu(self, avg_glucose):
        """پیشنهاد منوی غذایی ساده بر اساس میانگین قند خون"""
        if avg_glucose < 80:
            return "مصرف غذاهای پرکربوهیدرات با کنترل پزشک"
        elif avg_glucose > 180:
            return "پرهیز از قند و کربوهیدرات بالا، مصرف سبزیجات و پروتئین"
        else:
            return "رژیم متعادل با میوه، سبزیجات و غلات کامل"

    def ai_recognize_food(self, image_path):
        """تشخیص نوع غذا از روی عکس (نمونه - نیاز به ماژول AI واقعی)"""
        # در نسخه واقعی: استفاده از مدل AI برای تشخیص غذا
        # اینجا فقط نام فایل را به عنوان نام غذا بازمی‌گرداند
        import os
        name = os.path.splitext(os.path.basename(image_path))[0]
        # اگر نام غذا در پایگاه داده بود، همان را برگرداند
        for food in self.food_db.foods:
            if food in name:
                return food
        return None

    def run(self):
        """اجرای برنامه (حلقه اصلی)"""
        try:
            self.root.mainloop()
        except Exception as e:
            import logging
            logging.error(f"خطا در اجرای برنامه: {e}")
            raise

    def show_medical_features(self):
        """پنجره امکانات پزشکی پیشرفته (فاز ۳) با امکان حذف سوابق"""
        try:
            dialog = tk.Toplevel(self.root)
            dialog.title("امکانات پزشکی پیشرفته")
            dialog.geometry("400x650")
            dialog.configure(bg="#f0f0f0")

            ttk.Label(dialog, text="امکانات پزشکی:", font=self.default_font).pack(pady=10)
            ttk.Button(dialog, text="ارسال هشدار اورژانس", command=self.send_emergency_alert).pack(pady=8)
            ttk.Button(dialog, text="اتصال به پزشک (آنلاین)", command=self.connect_to_doctor).pack(pady=8)
            ttk.Button(dialog, text="یادآوری ویزیت بعدی", command=self.set_visit_reminder).pack(pady=8)
            ttk.Button(dialog, text="ثبت علائم جانبی", command=self.log_side_effects).pack(pady=8)
            ttk.Button(dialog, text="نسخه موبایل/ویجت (آزمایشی)", command=self.show_mobile_widget_info).pack(pady=8)

            # نمایش تاریخچه هشدار اورژانس با امکان حذف
            ttk.Label(dialog, text="تاریخچه هشدار اورژانس:", font=self.default_font).pack(pady=10)
            emergency_box = tk.Listbox(dialog, height=4, font=self.default_font)
            emergency_box.pack(fill="x", padx=10)
            for dt in getattr(self, 'emergency_history', []):
                emergency_box.insert(tk.END, dt)
            def delete_emergency():
                sel = emergency_box.curselection()
                if sel:
                    idx = sel[0]
                    if hasattr(self, 'emergency_history'):
                        del self.emergency_history[idx]
                        emergency_box.delete(idx)
            ttk.Button(dialog, text="حذف مورد انتخابی", command=delete_emergency).pack(pady=3)

            # نمایش تاریخچه علائم جانبی با امکان حذف
            ttk.Label(dialog, text="تاریخچه علائم جانبی:", font=self.default_font).pack(pady=10)
            side_box = tk.Listbox(dialog, height=6, font=self.default_font)
            side_box.pack(fill="x", padx=10)
            for dt, txt in getattr(self, 'side_effects_history', []):
                side_box.insert(tk.END, f"{dt}: {txt}")
            def delete_side_effect():
                sel = side_box.curselection()
                if sel:
                    idx = sel[0]
                    if hasattr(self, 'side_effects_history'):
                        del self.side_effects_history[idx]
                        side_box.delete(idx)
            ttk.Button(dialog, text="حذف مورد انتخابی", command=delete_side_effect).pack(pady=3)
        except Exception as e:
            logging.error(f"خطا در امکانات پزشکی: {e}")
            messagebox.showerror("خطا", f"خطا در امکانات پزشکی: {e}")

    def send_emergency_alert(self):
        """ارسال هشدار اورژانس و ثبت در تاریخچه"""
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        if not hasattr(self, 'emergency_history'):
            self.emergency_history = []
        self.emergency_history.append(now)
        messagebox.showinfo("هشدار اورژانس", f"هشدار اورژانس ارسال شد!\nزمان: {now}")

    def connect_to_doctor(self):
        """اتصال به پزشک آنلاین (نمونه)"""
        messagebox.showinfo("اتصال به پزشک", "در حال اتصال به پزشک... (نمونه)")

    def set_visit_reminder(self):
        """ثبت یادآوری ویزیت با انتخاب تاریخ و ساعت"""
        import datetime
        dialog = tk.Toplevel(self.root)
        dialog.title("یادآوری ویزیت")
        dialog.geometry("350x200")
        dialog.configure(bg="#f0f0f0")
        ttk.Label(dialog, text="تاریخ ویزیت (YYYY-MM-DD):", font=self.default_font).pack(pady=5)
        date_entry = ttk.Entry(dialog, font=self.default_font)
        date_entry.pack(pady=5)
        ttk.Label(dialog, text="ساعت (HH:MM):", font=self.default_font).pack(pady=5)
        time_entry = ttk.Entry(dialog, font=self.default_font)
        time_entry.pack(pady=5)
        def save_reminder():
            date = date_entry.get().strip()
            time = time_entry.get().strip()
            try:
                datetime.datetime.strptime(date, "%Y-%m-%d")
                datetime.datetime.strptime(time, "%H:%M")
                messagebox.showinfo("یادآوری ثبت شد", f"ویزیت بعدی: {date} ساعت {time}")
                dialog.destroy()
            except Exception:
                messagebox.showerror("خطا", "فرمت تاریخ یا ساعت صحیح نیست.")
        ttk.Button(dialog, text="ثبت یادآوری", command=save_reminder).pack(pady=10)

    def log_side_effects(self):
        """ثبت علائم جانبی و نمایش تاریخچه"""
        from datetime import datetime
        if not hasattr(self, 'side_effects_history'):
            self.side_effects_history = []
        dialog = tk.Toplevel(self.root)
        dialog.title("ثبت علائم جانبی")
        dialog.geometry("400x350")
        dialog.configure(bg="#f0f0f0")
        ttk.Label(dialog, text="علائم جانبی را وارد کنید:", font=self.default_font).pack(pady=10)
        entry = ttk.Entry(dialog, font=self.default_font, width=40)
        entry.pack(pady=5)
        def save_effect():
            text = entry.get().strip()
            if text:
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.side_effects_history.append((now, text))
                messagebox.showinfo("ثبت شد", "علائم جانبی ثبت شد.")
                entry.delete(0, tk.END)
                update_history()
        ttk.Button(dialog, text="ثبت", command=save_effect).pack(pady=5)
        ttk.Label(dialog, text="تاریخچه علائم:", font=self.default_font).pack(pady=10)
        history_box = tk.Text(dialog, height=8, font=self.default_font)
        history_box.pack(fill="both", expand=True, padx=10)
        def update_history():
            history_box.delete(1.0, tk.END)
            for dt, txt in getattr(self, 'side_effects_history', []):
                history_box.insert(tk.END, f"{dt}: {txt}\n")
        update_history()

    def show_mobile_widget_info(self):
        """نمایش اطلاعات نسخه موبایل/ویجت (نمونه)"""
        messagebox.showinfo("نسخه موبایل/ویجت", "نسخه موبایل و ویجت در دست توسعه است.")

    def show_settings_dialog(self):
        """پنجره تنظیمات شخصی‌سازی و تجربه کاربری"""
        import json
        dialog = tk.Toplevel(self.root)
        dialog.title("تنظیمات شخصی‌سازی")
        dialog.geometry("400x400")
        dialog.configure(bg="#f0f0f0")

        # رنگ پس‌زمینه
        ttk.Label(dialog, text="رنگ پس‌زمینه:", font=self.default_font).pack(pady=5)
        color_var = tk.StringVar(value=self.root['bg'])
        color_entry = ttk.Entry(dialog, textvariable=color_var, font=self.default_font)
        color_entry.pack(pady=5)

        # فونت
        ttk.Label(dialog, text="فونت:", font=self.default_font).pack(pady=5)
        font_var = tk.StringVar(value=self.default_font[0])
        font_entry = ttk.Entry(dialog, textvariable=font_var, font=self.default_font)
        font_entry.pack(pady=5)

        # هشدار صوتی
        sound_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dialog, text="فعال‌سازی هشدار صوتی", variable=sound_var).pack(pady=5)

        # دکمه ذخیره
        def save_settings():
            settings = {
                'bg_color': color_var.get(),
                'font': font_var.get(),
                'sound': sound_var.get()
            }
            with open('user_settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.apply_user_settings(settings)
            messagebox.showinfo("ذخیره شد", "تنظیمات ذخیره شد.")
            dialog.destroy()
        ttk.Button(dialog, text="ذخیره تنظیمات", command=save_settings).pack(pady=20)

    def apply_user_settings(self, settings):
        """اعمال تنظیمات شخصی‌سازی"""
        self.root.configure(bg=settings.get('bg_color', '#f0f0f0'))
        self.default_font = (settings.get('font', 'Tahoma'), 10)
        # (در صورت نیاز: بازآفرینی ویجت‌ها با فونت جدید)

    def load_user_settings(self):
        """بارگذاری تنظیمات کاربر از فایل"""
        import json
        try:
            with open('user_settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
            self.apply_user_settings(settings)
        except Exception:
            pass

    # فراخوانی در __init__:
    # self.load_user_settings()

    # افزودن گزینه به منوی اصلی:
    # menu = tk.Menu(self.root)
    # self.root.config(menu=menu)
    # settings_menu = tk.Menu(menu, tearoff=0)
    # menu.add_cascade(label="تنظیمات", menu=settings_menu)
    # settings_menu.add_command(label="شخصی‌سازی...", command=self.show_settings_dialog)
