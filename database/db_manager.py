#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مدیریت پایگاه داده برای سیستم مدیریت قند خون
"""

import sqlite3
import logging
from datetime import datetime, timedelta
import os
from .models import User, Reading, Reminder, Prediction

class DatabaseManager:
    def __init__(self, db_name="glucose_readings.db"):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        """ایجاد پایگاه داده و جداول"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # بررسی وجود جدول users و اعمال تغییرات schema در صورت نیاز
                cursor.execute("PRAGMA table_info(users)")
                columns = [col[1] for col in cursor.fetchall()]

                if 'users' not in columns: # اگر جدول وجود ندارد، آن را ایجاد کن
                    cursor.execute('''
                        CREATE TABLE users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL DEFAULT 'کاربر پیش‌فرض',
                            age INTEGER DEFAULT 30,
                            gender TEXT DEFAULT 'نامشخص',
                            target_glucose_min INTEGER DEFAULT 80,
                            target_glucose_max INTEGER DEFAULT 140,
                            created_at TEXT DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                else: # اگر جدول وجود دارد، schema را بررسی و به‌روزرسانی کن
                    # افزودن ستون‌های جدید در صورت عدم وجود
                    if 'username' not in columns:
                        cursor.execute("ALTER TABLE users ADD COLUMN username TEXT DEFAULT 'کاربر پیش‌فرض'")
                    if 'gender' not in columns:
                        cursor.execute("ALTER TABLE users ADD COLUMN gender TEXT DEFAULT 'نامشخص'")
                    if 'target_glucose_min' not in columns:
                        cursor.execute("ALTER TABLE users ADD COLUMN target_glucose_min INTEGER DEFAULT 80")
                    if 'target_glucose_max' not in columns:
                        cursor.execute("ALTER TABLE users ADD COLUMN target_glucose_max INTEGER DEFAULT 140")
                    
                    # حذف ستون‌های قدیمی در صورت وجود (اگر قبلاً وجود داشته‌اند)
                    # SQLite از DROP COLUMN مستقیم پشتیبانی نمی‌کند، باید جدول را بازسازی کرد.
                    # برای سادگی، فعلاً فقط ستون‌های جدید را اضافه می‌کنیم و فرض می‌کنیم
                    # ستون‌های قدیمی (weight, height, diabetes_type) در کد استفاده نمی‌شوند.
                    # اگر نیاز به حذف فیزیکی باشد، باید یک جدول موقت ایجاد و داده‌ها را منتقل کرد.
                    # این کار پیچیده‌تر است و برای این پروژه فعلاً از آن صرف‌نظر می‌کنیم.
                    
                    # اطمینان از وجود ستون‌های مورد نیاز برای UserSettingsTab
                    # اگر ستون name وجود دارد و username وجود ندارد، name را به username تغییر نام دهید
                    if 'name' in columns and 'username' not in columns:
                        cursor.execute("ALTER TABLE users RENAME COLUMN name TO username")
                    
                    # اگر ستون‌های قدیمی هنوز وجود دارند، می‌توانیم آن‌ها را نادیده بگیریم
                    # یا یک فرآیند مهاجرت پیچیده‌تر را پیاده‌سازی کنیم.
                    # برای این پروژه، فرض می‌کنیم که این ستون‌ها دیگر در مدل User استفاده نمی‌شوند.

                # جدول خوانش‌ها
                
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

    def fetch_readings_by_date_range(self, start_date, end_date, user_id=1):
        """دریافت خوانش‌ها بر اساس محدوده تاریخ شمسی"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM readings WHERE user_id = ? AND jalali_date BETWEEN ? AND ?
                    ORDER BY jalali_date DESC, time DESC
                ''', (user_id, start_date, end_date))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"خطا در دریافت خوانش‌ها بر اساس محدوده تاریخ: {e}")
            return []

    def get_user_settings(self, user_id=1):
        """دریافت تنظیمات کاربر"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                user_data = cursor.fetchone()
                if user_data:
                    # فرض می‌کنیم User مدل مناسبی برای نگهداری این اطلاعات است
                    # یا یک مدل جدید UserSettings ایجاد می‌کنیم
                    return User(
                        id=user_data[0],
                        username=user_data[1],
                        age=user_data[2],
                        gender=user_data[3],
                        target_glucose_min=user_data[4],
                        target_glucose_max=user_data[5]
                    )
                return None
        except Exception as e:
            logging.error(f"خطا در دریافت تنظیمات کاربر: {e}")
            return None

    def save_user_settings(self, username, age, gender, target_glucose_min, target_glucose_max, user_id=1):
        """ذخیره یا به‌روزرسانی تنظیمات کاربر"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users WHERE id = ?", (user_id,))
                if cursor.fetchone()[0] > 0:
                    # به‌روزرسانی کاربر موجود
                    cursor.execute('''
                        UPDATE users SET 
                        username = ?, age = ?, gender = ?, target_glucose_min = ?, target_glucose_max = ?
                        WHERE id = ?
                    ''', (username, age, gender, target_glucose_min, target_glucose_max, user_id))
                else:
                    # درج کاربر جدید (اگر user_id 1 باشد و وجود نداشته باشد)
                    cursor.execute('''
                        INSERT INTO users 
                        (id, username, age, gender, target_glucose_min, target_glucose_max)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (user_id, username, age, gender, target_glucose_min, target_glucose_max))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"خطا در ذخیره تنظیمات کاربر: {e}")
            return False

    def insert_reminder(self, title, scheduled_time, message="", user_id=1, reminder_type="اندازه‌گیری", frequency="روزانه"):
        """درج یادآوری جدید"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO reminders 
                    (user_id, title, message, reminder_type, scheduled_time, frequency)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, title, message, reminder_type, scheduled_time, frequency))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"خطا در درج یادآوری: {e}")
            return False

    def fetch_all_reminders(self, user_id=1):
        """دریافت تمام یادآوری‌ها"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM reminders WHERE user_id = ? 
                    ORDER BY scheduled_time
                ''', (user_id,))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"خطا در دریافت یادآوری‌ها: {e}")
            return []

    def toggle_reminder(self, reminder_id):
        """تغییر وضعیت فعال/غیرفعال یادآوری"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT is_active FROM reminders WHERE id = ?", (reminder_id,))
                current_status = cursor.fetchone()[0]
                new_status = 0 if current_status else 1
                
                conn.execute("UPDATE reminders SET is_active = ? WHERE id = ?", (new_status, reminder_id))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"خطا در تغییر وضعیت یادآوری: {e}")
            return False

    def delete_reminder(self, reminder_id):
        """حذف یادآوری"""
        try:
            with self.get_connection() as conn:
                conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"خطا در حذف یادآوری: {e}")
            return False

    def insert_prediction(self, user_id, prediction_date, predicted_glucose, confidence_score=0.5):
        """درج پیش‌بینی جدید"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO predictions 
                    (user_id, prediction_date, predicted_glucose, confidence_score)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, prediction_date, predicted_glucose, confidence_score))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"خطا در درج پیش‌بینی: {e}")
            return False

    def fetch_recent_predictions(self, days=7, user_id=1):
        """دریافت پیش‌بینی‌های اخیر"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM predictions 
                    WHERE user_id = ? AND prediction_date >= ?
                    ORDER BY prediction_date DESC
                ''', (user_id, cutoff_date))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"خطا در دریافت پیش‌بینی‌ها: {e}")
            return []

    def close(self):
        """بستن اتصال"""
        pass