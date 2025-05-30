#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سیستم پیشرفته مدیریت قند خون
نسخه 2.0
"""

import os
import sys
import logging
from datetime import datetime

# اضافه کردن مسیرهای مورد نیاز
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# تنظیمات لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class GlucoseManagementSystem:
    def __init__(self):
        """مقداردهی اولیه سیستم مدیریت قند خون"""
        logger.info("در حال راه‌اندازی سیستم مدیریت قند خون...")
        
        # ایجاد پوشه‌های مورد نیاز
        self._create_directories()
        
        # راه‌اندازی ماژول‌های اصلی
        self._init_modules()
        
    def _create_directories(self):
        """ایجاد پوشه‌های مورد نیاز"""
        directories = [
            'core',
            'ai',
            'ui',
            'devices',
            'analytics',
            'utils',
            'logs',
            'data',
            'config',
            'models'
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"پوشه {directory} ایجاد شد")
                
    def _init_modules(self):
        """راه‌اندازی ماژول‌های اصلی"""
        try:
            # در اینجا ماژول‌های اصلی را import و مقداردهی اولیه می‌کنیم
            from core.config_manager import ConfigManager
            from core.database_manager import DatabaseManager
            from ui.main_window import MainWindow
            
            # ایجاد تنظیمات
            self.config = ConfigManager()
            
            # ایجاد پایگاه داده
            self.db_manager = DatabaseManager(self.config['DATABASE']['name'])
            
            # ایجاد کاربر پیش‌فرض اگر وجود نداشته باشد
            if not self.db_manager.get_user(1):
                self.db_manager.add_user("کاربر پیش‌فرض")
                self.db_manager.update_user_settings(1, {
                    'language': 'fa',
                    'theme': 'default',
                    'notification_enabled': True
                })
            
            # ایجاد پنجره اصلی
            self.main_window = MainWindow(self)
            
            logger.info("ماژول‌های اصلی با موفقیت راه‌اندازی شدند")
            
        except Exception as e:
            logger.error(f"خطا در راه‌اندازی ماژول‌ها: {str(e)}")
            raise
            
    def run(self):
        """اجرای برنامه"""
        try:
            logger.info("در حال اجرای برنامه...")
            self.main_window.run()
        except Exception as e:
            logger.error(f"خطا در اجرای برنامه: {str(e)}")
            raise
        finally:
            if hasattr(self, 'db_manager'):
                self.db_manager.close()

if __name__ == "__main__":
    try:
        app = GlucoseManagementSystem()
        app.run()
    except Exception as e:
        logger.critical(f"خطای بحرانی در اجرای برنامه: {str(e)}")
        sys.exit(1)