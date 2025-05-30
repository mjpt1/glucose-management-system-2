#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
توابع اعتبارسنجی ورودی‌ها
"""

import re
from typing import Tuple, Optional

def validate_glucose_level(level: str) -> Tuple[bool, Optional[int]]:
    """
    اعتبارسنجی سطح قند خون
    
    Args:
        level (str): سطح قند خون
        
    Returns:
        Tuple[bool, Optional[int]]: (معتبر بودن، مقدار عددی)
    """
    try:
        value = int(level)
        if 20 <= value <= 600:  # محدوده منطقی برای قند خون
            return True, value
        return False, None
    except ValueError:
        return False, None

def validate_name(name: str) -> bool:
    """
    اعتبارسنجی نام
    
    Args:
        name (str): نام
        
    Returns:
        bool: True اگر نام معتبر باشد، False در غیر این صورت
    """
    if not name or len(name.strip()) < 2:
        return False
    # فقط حروف فارسی، انگلیسی، اعداد و فاصله
    pattern = r'^[\u0600-\u06FF\u0750-\u077Fa-zA-Z0-9\s]+$'
    return bool(re.match(pattern, name))

def validate_age(age: str) -> Tuple[bool, Optional[int]]:
    """
    اعتبارسنجی سن
    
    Args:
        age (str): سن
        
    Returns:
        Tuple[bool, Optional[int]]: (معتبر بودن، مقدار عددی)
    """
    try:
        value = int(age)
        if 1 <= value <= 120:  # محدوده منطقی برای سن
            return True, value
        return False, None
    except ValueError:
        return False, None

def validate_weight(weight: str) -> Tuple[bool, Optional[float]]:
    """
    اعتبارسنجی وزن
    
    Args:
        weight (str): وزن
        
    Returns:
        Tuple[bool, Optional[float]]: (معتبر بودن، مقدار عددی)
    """
    try:
        value = float(weight)
        if 20 <= value <= 300:  # محدوده منطقی برای وزن (کیلوگرم)
            return True, value
        return False, None
    except ValueError:
        return False, None

def validate_height(height: str) -> Tuple[bool, Optional[float]]:
    """
    اعتبارسنجی قد
    
    Args:
        height (str): قد
        
    Returns:
        Tuple[bool, Optional[float]]: (معتبر بودن، مقدار عددی)
    """
    try:
        value = float(height)
        if 50 <= value <= 250:  # محدوده منطقی برای قد (سانتی‌متر)
            return True, value
        return False, None
    except ValueError:
        return False, None

def validate_diabetes_type(diabetes_type: str) -> bool:
    """
    اعتبارسنجی نوع دیابت
    
    Args:
        diabetes_type (str): نوع دیابت
        
    Returns:
        bool: True اگر نوع دیابت معتبر باشد، False در غیر این صورت
    """
    valid_types = ['نوع 1', 'نوع 2', 'بارداری', 'پیش‌دیابت', 'سایر']
    return diabetes_type in valid_types

def validate_target_range(min_value: str, max_value: str) -> Tuple[bool, Optional[int], Optional[int]]:
    """
    اعتبارسنجی محدوده هدف قند خون
    
    Args:
        min_value (str): حداقل مقدار
        max_value (str): حداکثر مقدار
        
    Returns:
        Tuple[bool, Optional[int], Optional[int]]: (معتبر بودن، حداقل، حداکثر)
    """
    try:
        min_val = int(min_value)
        max_val = int(max_value)
        
        if 50 <= min_val <= 200 and 50 <= max_val <= 200 and min_val < max_val:
            return True, min_val, max_val
        return False, None, None
    except ValueError:
        return False, None, None

def validate_meal_status(status: str) -> bool:
    """
    اعتبارسنجی وضعیت وعده غذایی
    
    Args:
        status (str): وضعیت وعده غذایی
        
    Returns:
        bool: True اگر وضعیت معتبر باشد، False در غیر این صورت
    """
    valid_statuses = ['قبل از صبحانه', 'بعد از صبحانه', 'قبل از نهار', 'بعد از نهار',
                     'قبل از شام', 'بعد از شام', 'قبل از خواب', 'نامعلوم']
    return status in valid_statuses

def validate_mood(mood: str) -> bool:
    """
    اعتبارسنجی وضعیت روحی
    
    Args:
        mood (str): وضعیت روحی
        
    Returns:
        bool: True اگر وضعیت معتبر باشد، False در غیر این صورت
    """
    valid_moods = ['عالی', 'خوب', 'متوسط', 'بد', 'خیلی بد']
    return mood in valid_moods

def validate_stress_level(level: str) -> Tuple[bool, Optional[int]]:
    """
    اعتبارسنجی سطح استرس
    
    Args:
        level (str): سطح استرس
        
    Returns:
        Tuple[bool, Optional[int]]: (معتبر بودن، مقدار عددی)
    """
    try:
        value = int(level)
        if 1 <= value <= 10:  # مقیاس 1 تا 10
            return True, value
        return False, None
    except ValueError:
        return False, None

def validate_exercise_minutes(minutes: str) -> Tuple[bool, Optional[int]]:
    """
    اعتبارسنجی دقایق ورزش
    
    Args:
        minutes (str): دقایق ورزش
        
    Returns:
        Tuple[bool, Optional[int]]: (معتبر بودن، مقدار عددی)
    """
    try:
        value = int(minutes)
        if 0 <= value <= 480:  # حداکثر 8 ساعت
            return True, value
        return False, None
    except ValueError:
        return False, None

def validate_sleep_hours(hours: str) -> Tuple[bool, Optional[float]]:
    """
    اعتبارسنجی ساعات خواب
    
    Args:
        hours (str): ساعات خواب
        
    Returns:
        Tuple[bool, Optional[float]]: (معتبر بودن، مقدار عددی)
    """
    try:
        value = float(hours)
        if 0 <= value <= 24:  # محدوده منطقی برای خواب
            return True, value
        return False, None
    except ValueError:
        return False, None 