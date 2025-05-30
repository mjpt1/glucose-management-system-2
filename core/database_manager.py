#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مدیریت پایگاه داده SQLite
"""

import os
import sqlite3
import logging
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class DatabaseManager:
    """کلاس مدیریت پایگاه داده"""
    
    def __init__(self, db_name: str = "data/glucose.db"):
        """مقداردهی اولیه مدیر پایگاه داده"""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        
        # ایجاد پوشه data اگر وجود نداشته باشد
        os.makedirs(os.path.dirname(db_name), exist_ok=True)
        
        # اتصال به پایگاه داده
        self._connect()
        
        # ایجاد جداول
        self._create_tables()
        
    def _connect(self) -> None:
        """اتصال به پایگاه داده"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            logger.info(f"اتصال به پایگاه داده {self.db_name} برقرار شد")
        except Exception as e:
            logger.error(f"خطا در اتصال به پایگاه داده: {str(e)}")
            raise
            
    def _create_tables(self) -> None:
        """ایجاد جداول مورد نیاز"""
        try:
            # جدول خوانش‌های قند خون
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS glucose_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    value REAL NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول کاربران
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول یادآوری‌ها
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    time TEXT NOT NULL,
                    repeat TEXT NOT NULL,
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول تنظیمات کاربر
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    language TEXT DEFAULT 'fa',
                    theme TEXT DEFAULT 'default',
                    notification_enabled BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            self.conn.commit()
            logger.info("جداول پایگاه داده ایجاد شدند")
            
        except Exception as e:
            logger.error(f"خطا در ایجاد جداول: {str(e)}")
            raise
            
    def add_glucose_reading(self, value: float, date: str, time: str, note: str = "") -> int:
        """افزودن خوانش قند خون جدید"""
        try:
            self.cursor.execute("""
                INSERT INTO glucose_readings (value, date, time, note)
                VALUES (?, ?, ?, ?)
            """, (value, date, time, note))
            
            self.conn.commit()
            reading_id = self.cursor.lastrowid
            logger.info(f"خوانش قند خون جدید با شناسه {reading_id} ثبت شد")
            return reading_id
            
        except Exception as e:
            logger.error(f"خطا در ثبت خوانش قند خون: {str(e)}")
            raise
            
    def get_glucose_readings(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """دریافت خوانش‌های قند خون"""
        try:
            query = "SELECT * FROM glucose_readings"
            params = []
            
            # اعمال فیلترها
            if start_date or end_date:
                conditions = []
                if start_date:
                    conditions.append("date >= ?")
                    params.append(start_date)
                if end_date:
                    conditions.append("date <= ?")
                    params.append(end_date)
                query += " WHERE " + " AND ".join(conditions)
                
            # مرتب‌سازی
            query += " ORDER BY date DESC, time DESC"
            
            # محدودیت تعداد
            if limit:
                query += " LIMIT ?"
                params.append(limit)
                
            self.cursor.execute(query, params)
            readings = [dict(row) for row in self.cursor.fetchall()]
            
            return readings
            
        except Exception as e:
            logger.error(f"خطا در دریافت خوانش‌های قند خون: {str(e)}")
            raise
            
    def add_user(self, name: str) -> int:
        """افزودن کاربر جدید"""
        try:
            self.cursor.execute("""
                INSERT INTO users (name)
                VALUES (?)
            """, (name,))
            
            self.conn.commit()
            user_id = self.cursor.lastrowid
            logger.info(f"کاربر جدید با شناسه {user_id} ایجاد شد")
            return user_id
            
        except Exception as e:
            logger.error(f"خطا در ایجاد کاربر: {str(e)}")
            raise
            
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """دریافت اطلاعات کاربر"""
        try:
            self.cursor.execute("""
                SELECT * FROM users
                WHERE id = ?
            """, (user_id,))
            
            user = self.cursor.fetchone()
            return dict(user) if user else None
            
        except Exception as e:
            logger.error(f"خطا در دریافت اطلاعات کاربر: {str(e)}")
            raise
            
    def add_reminder(self, title: str, time: str, repeat: str) -> int:
        """افزودن یادآوری جدید"""
        try:
            self.cursor.execute("""
                INSERT INTO reminders (title, time, repeat)
                VALUES (?, ?, ?)
            """, (title, time, repeat))
            
            self.conn.commit()
            reminder_id = self.cursor.lastrowid
            logger.info(f"یادآوری جدید با شناسه {reminder_id} ایجاد شد")
            return reminder_id
            
        except Exception as e:
            logger.error(f"خطا در ایجاد یادآوری: {str(e)}")
            raise
            
    def get_reminders(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """دریافت یادآوری‌ها"""
        try:
            query = "SELECT * FROM reminders"
            params = []
            
            if active_only:
                query += " WHERE active = 1"
                
            query += " ORDER BY time"
            
            self.cursor.execute(query, params)
            reminders = [dict(row) for row in self.cursor.fetchall()]
            
            return reminders
            
        except Exception as e:
            logger.error(f"خطا در دریافت یادآوری‌ها: {str(e)}")
            raise
            
    def update_user_settings(self, user_id: int, settings: Dict[str, Any]) -> None:
        """به‌روزرسانی تنظیمات کاربر"""
        try:
            # بررسی وجود کاربر
            if not self.get_user(user_id):
                raise ValueError(f"کاربر با شناسه {user_id} یافت نشد")
                
            # به‌روزرسانی تنظیمات
            self.cursor.execute("""
                INSERT OR REPLACE INTO user_settings
                (user_id, language, theme, notification_enabled)
                VALUES (?, ?, ?, ?)
            """, (
                user_id,
                settings.get('language', 'fa'),
                settings.get('theme', 'default'),
                settings.get('notification_enabled', True)
            ))
            
            self.conn.commit()
            logger.info(f"تنظیمات کاربر {user_id} به‌روزرسانی شد")
            
        except Exception as e:
            logger.error(f"خطا در به‌روزرسانی تنظیمات کاربر: {str(e)}")
            raise
            
    def get_user_settings(self, user_id: int) -> Optional[Dict[str, Any]]:
        """دریافت تنظیمات کاربر"""
        try:
            self.cursor.execute("""
                SELECT * FROM user_settings
                WHERE user_id = ?
            """, (user_id,))
            
            settings = self.cursor.fetchone()
            return dict(settings) if settings else None
            
        except Exception as e:
            logger.error(f"خطا در دریافت تنظیمات کاربر: {str(e)}")
            raise
            
    def backup_database(self, backup_dir: str = "data/backups") -> str:
        """پشتیبان‌گیری از پایگاه داده"""
        try:
            # ایجاد پوشه پشتیبان اگر وجود نداشته باشد
            os.makedirs(backup_dir, exist_ok=True)
            
            # نام فایل پشتیبان
            backup_file = os.path.join(
                backup_dir,
                f"glucose_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            )
            
            # کپی فایل پایگاه داده
            shutil.copy2(self.db_name, backup_file)
            
            logger.info(f"پشتیبان‌گیری از پایگاه داده در {backup_file} انجام شد")
            return backup_file
            
        except Exception as e:
            logger.error(f"خطا در پشتیبان‌گیری از پایگاه داده: {str(e)}")
            raise
            
    def close(self) -> None:
        """بستن اتصال به پایگاه داده"""
        try:
            if self.conn:
                self.conn.close()
                logger.info("اتصال به پایگاه داده بسته شد")
        except Exception as e:
            logger.error(f"خطا در بستن اتصال به پایگاه داده: {str(e)}")
            raise 