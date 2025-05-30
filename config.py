#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تنظیمات کلی سیستم مدیریت قند خون
"""

import os
import logging
import matplotlib.pyplot as plt

# مسیرهای پایه
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')
ICONS_DIR = os.path.join(RESOURCES_DIR, 'icons')
STYLES_DIR = os.path.join(RESOURCES_DIR, 'styles')

# تنظیمات اصلی برنامه
CONFIG = {
    # تنظیمات پایگاه داده
    'DATABASE': {
        'name': 'glucose_readings.db',
        'path': os.path.join(BASE_DIR, 'glucose_readings.db'),
    },

    # تنظیمات کاربر پیش‌فرض
    'DEFAULT_USER': {
        'username': 'کاربر پیش‌فرض',
        'age': 30,
        'gender': 'نامشخص',
        'target_glucose_min': 80,
        'target_glucose_max': 140,
    },

    # محدوده‌های قند خون
    'GLUCOSE_RANGES': {
        'dangerous_low': 70,
        'low': 80,
        'normal_min': 80,
        'normal_max': 140,
        'high': 180,
        'dangerous_high': 200,
    },

    # تنظیمات لاگ
    'LOGGING': {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(levelname)s - %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'standard',
                'filename': os.path.join(BASE_DIR, 'logs', 'app.log'),
                'encoding': 'utf-8',
                'maxBytes': 10485760, # 10 MB
                'backupCount': 5,
            },
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': True
            },
        },
    },

    # تنظیمات رابط کاربری
    'UI': {
        'title': 'مدیریت پیشرفته قند خون',
        'geometry': '1200x800',
        'default_font': ('Tahoma', 10),
        'header_font': ('Tahoma', 12, 'bold'),
        'bg_color': '#f0f0f0',
        'colors': {
            'primary': '#4a7abc',
            'secondary': '#5294e2',
            'accent': '#2ecc71',
            'text': '#333333',
            'background': '#f0f0f0',
            'border': '#cccccc'
        }
    },

    # تنظیمات نمودارها
    'CHART': {
        'figure_size': (10, 6),
        'dpi': 100,
        'font_family': 'Vazirmatn',
        'grid_alpha': 0.3,
    },

    # تنظیمات هوش مصنوعی
    'AI': {
        'min_readings_for_training': 10,
        'min_readings_for_analysis': 5,
        'confidence_threshold': 0.6,
    },

    # تنظیمات تشخیص غذا
    'FOOD_RECOGNITION': {
        'model_path': os.path.join(RESOURCES_DIR, 'models', 'food_recognition_model.h5'),
        'labels_path': os.path.join(RESOURCES_DIR, 'models', 'food_labels.json'),
        'confidence_threshold': 0.7,
        'image_size': (224, 224),
    },

    # تنظیمات دستگاه‌های پزشکی
    'MEDICAL_DEVICE': {
        'scan_interval': 5,  # ثانیه
        'timeout': 10,      # ثانیه
        'auto_connect': True,
    },

    # فیلدهای مربوط به خوانش قند خون
    'READING_FIELDS': {
        'meal_status_options': ['قبل از غذا', 'بعد از صبحانه', 'بعد از ناهار', 'بعد از شام', 'ناشتا', 'سایر'],
        'mood_options': ['عالی', 'خوب', 'متوسط', 'بد', 'خیلی بد'],
    },
    'REPORT_TAB_COLUMNS': [
        {'id': 'date_shamsi', 'name': 'تاریخ شمسی', 'text': 'تاریخ شمسی', 'width': 100, 'anchor': 'center'},
        {'id': 'date_miladi', 'name': 'تاریخ میلادی', 'text': 'تاریخ میلادی', 'width': 100, 'anchor': 'center'},
        {'id': 'time', 'name': 'زمان', 'text': 'زمان', 'width': 70, 'anchor': 'center'},
        {'id': 'glucose_level', 'name': 'سطح قند', 'text': 'سطح قند', 'width': 80, 'anchor': 'center'},
        {'id': 'meal_status', 'name': 'وضعیت غذا', 'text': 'وضعیت غذا', 'width': 100, 'anchor': 'center'},
        {'id': 'mood', 'name': 'خلق و خو', 'text': 'خلق و خو', 'width': 80, 'anchor': 'center'},
        {'id': 'stress', 'name': 'استرس', 'text': 'استرس', 'width': 60, 'anchor': 'center'},
        {'id': 'exercise_minutes', 'name': 'ورزش (دقیقه)', 'text': 'ورزش (دقیقه)', 'width': 100, 'anchor': 'center'},
        {'id': 'sleep_hours', 'name': 'خواب (ساعت)', 'text': 'خواب (ساعت)', 'width': 100, 'anchor': 'center'},
        {'id': 'description', 'name': 'توضیحات', 'text': 'توضیحات', 'width': 200, 'anchor': 'w'},
        {'id': 'status', 'name': 'وضعیت', 'text': 'وضعیت', 'width': 80, 'anchor': 'center'}
    ]
}


# تنظیم matplotlib برای فارسی
plt.rcParams['font.family'] = [CONFIG['CHART']['font_family']]
plt.rcParams['axes.unicode_minus'] = False