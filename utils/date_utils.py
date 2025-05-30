#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
توابع کمکی برای کار با تاریخ و زمان
"""

import jdatetime
from datetime import datetime, timedelta
from typing import Tuple, Optional

def get_current_datetime() -> Tuple[str, str, str]:
    """
    دریافت تاریخ و زمان فعلی به فرمت‌های مختلف
    
    Returns:
        Tuple[str, str, str]: (تاریخ میلادی، تاریخ شمسی، زمان)
    """
    now = datetime.now()
    jalali = jdatetime.datetime.fromgregorian(datetime=now)
    
    gregorian_date = now.strftime("%Y-%m-%d")
    jalali_date = jalali.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M")
    
    return gregorian_date, jalali_date, time

def jalali_to_gregorian(jalali_date: str) -> Optional[str]:
    """
    تبدیل تاریخ شمسی به میلادی
    
    Args:
        jalali_date (str): تاریخ شمسی به فرمت YYYY-MM-DD
        
    Returns:
        Optional[str]: تاریخ میلادی به فرمت YYYY-MM-DD یا None در صورت خطا
    """
    try:
        year, month, day = map(int, jalali_date.split('-'))
        jalali = jdatetime.date(year, month, day)
        gregorian = jalali.togregorian()
        return gregorian.strftime("%Y-%m-%d")
    except Exception:
        return None

def gregorian_to_jalali(gregorian_date: str) -> Optional[str]:
    """
    تبدیل تاریخ میلادی به شمسی
    
    Args:
        gregorian_date (str): تاریخ میلادی به فرمت YYYY-MM-DD
        
    Returns:
        Optional[str]: تاریخ شمسی به فرمت YYYY-MM-DD یا None در صورت خطا
    """
    try:
        year, month, day = map(int, gregorian_date.split('-'))
        gregorian = datetime(year, month, day)
        jalali = jdatetime.date.fromgregorian(datetime=gregorian)
        return jalali.strftime("%Y-%m-%d")
    except Exception:
        return None

def validate_jalali_date(date_str: str) -> bool:
    """
    اعتبارسنجی تاریخ شمسی
    
    Args:
        date_str (str): تاریخ شمسی به فرمت YYYY-MM-DD
        
    Returns:
        bool: True اگر تاریخ معتبر باشد، False در غیر این صورت
    """
    try:
        year, month, day = map(int, date_str.split('-'))
        jdatetime.date(year, month, day)
        return True
    except Exception:
        return False

def validate_time(time_str: str) -> bool:
    """
    اعتبارسنجی زمان
    
    Args:
        time_str (str): زمان به فرمت HH:MM
        
    Returns:
        bool: True اگر زمان معتبر باشد، False در غیر این صورت
    """
    try:
        hour, minute = map(int, time_str.split(':'))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return True
        return False
    except Exception:
        return False

def get_date_range(days: int) -> Tuple[str, str]:
    """
    دریافت محدوده تاریخ برای n روز گذشته
    
    Args:
        days (int): تعداد روزهای گذشته
        
    Returns:
        Tuple[str, str]: (تاریخ شروع، تاریخ پایان) به فرمت YYYY-MM-DD
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

def format_datetime(gregorian_date: str, time: str) -> str:
    """
    فرمت‌بندی تاریخ و زمان برای نمایش
    
    Args:
        gregorian_date (str): تاریخ میلادی به فرمت YYYY-MM-DD
        time (str): زمان به فرمت HH:MM
        
    Returns:
        str: رشته فرمت‌شده تاریخ و زمان
    """
    try:
        date_obj = datetime.strptime(gregorian_date, "%Y-%m-%d")
        jalali = jdatetime.datetime.fromgregorian(datetime=date_obj)
        return f"{jalali.strftime('%Y/%m/%d')} {time}"
    except Exception:
        return f"{gregorian_date} {time}" 