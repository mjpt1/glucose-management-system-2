#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مدیریت لاگ‌های سیستم
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional

def setup_logging(
    log_dir: str = "logs",
    log_level: int = logging.INFO,
    max_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    راه‌اندازی سیستم لاگینگ
    
    Args:
        log_dir (str): مسیر پوشه لاگ‌ها
        log_level (int): سطح لاگینگ
        max_size (int): حداکثر اندازه فایل لاگ
        backup_count (int): تعداد فایل‌های پشتیبان
    """
    # ایجاد پوشه لاگ‌ها
    os.makedirs(log_dir, exist_ok=True)
    
    # تنظیم فرمت لاگ
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # تنظیم handler فایل
    log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # تنظیم handler کنسول
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # تنظیم logger اصلی
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # تنظیم logger‌های دیگر
    loggers = [
        'core',
        'ai',
        'ui',
        'devices',
        'analytics',
        'utils'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

def get_logger(name: str) -> logging.Logger:
    """
    دریافت logger با نام مشخص
    
    Args:
        name (str): نام logger
        
    Returns:
        logging.Logger: شیء logger
    """
    return logging.getLogger(name)

def log_error(logger: logging.Logger, error: Exception, context: Optional[str] = None) -> None:
    """
    ثبت خطا در لاگ
    
    Args:
        logger (logging.Logger): logger
        error (Exception): خطا
        context (Optional[str]): توضیحات اضافی
    """
    message = f"{context + ': ' if context else ''}{str(error)}"
    logger.error(message, exc_info=True)

def log_info(logger: logging.Logger, message: str) -> None:
    """
    ثبت اطلاعات در لاگ
    
    Args:
        logger (logging.Logger): logger
        message (str): پیام
    """
    logger.info(message)

def log_warning(logger: logging.Logger, message: str) -> None:
    """
    ثبت هشدار در لاگ
    
    Args:
        logger (logging.Logger): logger
        message (str): پیام
    """
    logger.warning(message)

def log_debug(logger: logging.Logger, message: str) -> None:
    """
    ثبت اطلاعات دیباگ در لاگ
    
    Args:
        logger (logging.Logger): logger
        message (str): پیام
    """
    logger.debug(message)

def log_critical(logger: logging.Logger, error: Exception, context: Optional[str] = None) -> None:
    """
    ثبت خطای بحرانی در لاگ
    
    Args:
        logger (logging.Logger): logger
        error (Exception): خطا
        context (Optional[str]): توضیحات اضافی
    """
    message = f"{context + ': ' if context else ''}{str(error)}"
    logger.critical(message, exc_info=True) 