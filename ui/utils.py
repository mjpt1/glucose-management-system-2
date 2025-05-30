#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
توابع کمکی رابط کاربری
"""

import re
import logging
import jdatetime
from tkinter import messagebox
from typing import Tuple, Optional
from tkinter import ttk

def create_persian_style(root):
    """
    ایجاد استایل فارسی برای ویجت‌ها
    
    Args:
        root: پنجره اصلی برنامه
    """
    try:
        style = ttk.Style(root)
        style.configure('TFrame', background='white')
        style.configure('TLabel', font=('Vazirmatn', 10), background='white')
        style.configure('TButton', font=('Vazirmatn', 10))
        style.configure('TEntry', font=('Vazirmatn', 10))
        style.configure('TCombobox', font=('Vazirmatn', 10))
        style.configure('Treeview', font=('Vazirmatn', 10))
        style.configure('Treeview.Heading', font=('Vazirmatn', 10, 'bold'))
        style.configure('TLabelframe', font=('Vazirmatn', 10))
        style.configure('TLabelframe.Label', font=('Vazirmatn', 10))
        style.configure('Status.TLabel', font=('Vazirmatn', 9))
        style.configure('Accent.TButton', font=('Vazirmatn', 10, 'bold'))
        return style
    except Exception as e:
        logging.error(f"خطا در ایجاد استایل فارسی: {e}")
        return ttk.Style(root)

def validate_persian_time(time_str: str) -> Tuple[bool, str]:
    """
    اعتبارسنجی زمان
    
    Args:
        time_str (str): رشته زمان به فرمت HH:MM
        
    Returns:
        Tuple[bool, str]: وضعیت اعتبارسنجی و پیام خطا
    """
    try:
        # بررسی فرمت زمان
        pattern = r'^\d{1,2}:\d{1,2}$'
        if not re.match(pattern, time_str):
            return False, "فرمت زمان باید HH:MM باشد"
        
        # تبدیل به اجزای زمان
        parts = time_str.split(':')
        hour = int(parts[0])
        minute = int(parts[1])
        
        # بررسی محدوده مقادیر
        if hour < 0 or hour > 23:
            return False, "ساعت باید بین 0 تا 23 باشد"
        
        if minute < 0 or minute > 59:
            return False, "دقیقه باید بین 0 تا 59 باشد"
        
        return True, ""
    except ValueError as e:
        return False, f"زمان نامعتبر: {str(e)}"
    except Exception as e:
        logging.error(f"خطا در اعتبارسنجی زمان: {e}")
        return False, "خطا در بررسی زمان"

def get_glucose_status(level: float, config: dict) -> Tuple[str, str]:
    """
    تعیین وضعیت قند خون
    
    Args:
        level (float): سطح قند خون
        config (dict): تنظیمات برنامه
        
    Returns:
        Tuple[str, str]: وضعیت و رنگ متناظر
    """
    try:
        glucose_level = float(level)
        
        if glucose_level < config['GLUCOSE_LEVELS']['DANGEROUS_LOW']:
            return "خطرناک پایین", config['COLORS']['DANGEROUS_LOW']
        elif glucose_level < config['GLUCOSE_LEVELS']['LOW']:
            return "پایین", config['COLORS']['LOW']
        elif glucose_level <= config['GLUCOSE_LEVELS']['NORMAL_HIGH']:
            return "نرمال", config['COLORS']['NORMAL']
        elif glucose_level <= config['GLUCOSE_LEVELS']['HIGH']:
            return "بالا", config['COLORS']['HIGH']
        else:
            return "خطرناک بالا", config['COLORS']['DANGEROUS_HIGH']
    except Exception as e:
        logging.error(f"خطا در تعیین وضعیت قند خون: {e}")
        return "نامشخص", "#CCCCCC"

def show_message(parent, title: str, message: str, message_type: str = "info") -> Optional[bool]:
    """
    نمایش پیام به کاربر
    
    Args:
        parent: پنجره والد
        title (str): عنوان پیام
        message (str): متن پیام
        message_type (str): نوع پیام (info, warning, error, question)
        
    Returns:
        Optional[bool]: نتیجه در صورت پرسش (yes/no)
    """
    try:
        if message_type == "info":
            messagebox.showinfo(title, message, parent=parent)
        elif message_type == "warning":
            messagebox.showwarning(title, message, parent=parent)
        elif message_type == "error":
            messagebox.showerror(title, message, parent=parent)
        elif message_type == "question":
            return messagebox.askquestion(title, message, parent=parent) == "yes"
        else:
            messagebox.showinfo(title, message, parent=parent)
    except Exception as e:
        logging.error(f"خطا در نمایش پیام: {e}")
        return None

def validate_persian_date(date_str: str) -> Tuple[bool, str]:
    """
    اعتبارسنجی تاریخ فارسی
    
    Args:
        date_str (str): رشته تاریخ به فرمت YYYY/MM/DD
        
    Returns:
        Tuple[bool, str]: وضعیت اعتبارسنجی و پیام خطا
    """
    try:
        # بررسی فرمت تاریخ
        pattern = r'^\d{4}/\d{1,2}/\d{1,2}$'
        if not re.match(pattern, date_str):
            return False, "فرمت تاریخ باید YYYY/MM/DD باشد"
        
        # تبدیل به اجزای تاریخ
        parts = date_str.split('/')
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
        
        # بررسی محدوده مقادیر
        if year < 1300 or year > 1500:
            return False, "سال باید بین 1300 تا 1500 باشد"
        
        if month < 1 or month > 12:
            return False, "ماه باید بین 1 تا 12 باشد"
        
        # بررسی روز با توجه به ماه
        if month <= 6:
            max_day = 31
        elif month <= 11:
            max_day = 30
        else:  # ماه 12
            # بررسی سال کبیسه
            if jdatetime.date(year, 1, 1).isleap():
                max_day = 30
            else:
                max_day = 29
        
        if day < 1 or day > max_day:
            return False, f"روز برای ماه {month} باید بین 1 تا {max_day} باشد"
        
        # تلاش برای ایجاد تاریخ معتبر
        jdatetime.date(year, month, day)
        
        return True, ""
    except ValueError as e:
        return False, f"تاریخ نامعتبر: {str(e)}"
    except Exception as e:
        logging.error(f"خطا در اعتبارسنجی تاریخ: {e}")
        return False, "خطا در بررسی تاریخ" 