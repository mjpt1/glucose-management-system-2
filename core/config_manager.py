#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مدیریت تنظیمات برنامه
"""

import os
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """کلاس مدیریت تنظیمات"""
    
    def __init__(self, config_file: str = "config/default_config.json"):
        """مقداردهی اولیه مدیر تنظیمات"""
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """بارگذاری تنظیمات از فایل"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"تنظیمات از فایل {self.config_file} بارگذاری شد")
            else:
                # ایجاد فایل تنظیمات پیش‌فرض
                config = {
                    "UI": {
                        "title": "سیستم مدیریت قند خون",
                        "window_size": "800x600",
                        "theme": "default",
                        "language": "fa",
                        "font_family": "Vazirmatn",
                        "font_size": 10
                    },
                    "DATABASE": {
                        "name": "data/glucose.db",
                        "backup_dir": "data/backups",
                        "backup_interval": 7
                    },
                    "GLUCOSE_LEVELS": {
                        "low": 70,
                        "normal_min": 70,
                        "normal_max": 140,
                        "high": 140
                    },
                    "COLORS": {
                        "low": "#ff6b6b",
                        "normal": "#51cf66",
                        "high": "#ff922b",
                        "background": "#ffffff",
                        "text": "#212529",
                        "primary": "#228be6",
                        "secondary": "#868e96"
                    },
                    "AI": {
                        "model_path": "models/glucose_predictor.joblib",
                        "scaler_path": "models/scaler.joblib",
                        "training_interval": 7,
                        "prediction_confidence_threshold": 0.7
                    },
                    "REMINDERS": {
                        "check_interval": 60,
                        "notification_duration": 5,
                        "sound_enabled": true
                    },
                    "EXPORT": {
                        "formats": ["csv", "pdf", "excel"],
                        "default_format": "csv",
                        "date_format": "%Y/%m/%d",
                        "time_format": "%H:%M"
                    }
                }
                
                # ایجاد پوشه config اگر وجود نداشته باشد
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                
                # ذخیره تنظیمات پیش‌فرض
                self.save_config(config)
                logger.info(f"فایل تنظیمات پیش‌فرض در {self.config_file} ایجاد شد")
                
            return config
            
        except Exception as e:
            logger.error(f"خطا در بارگذاری تنظیمات: {str(e)}")
            raise
            
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        """ذخیره تنظیمات در فایل"""
        try:
            if config is None:
                config = self.config
                
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
                
            logger.info(f"تنظیمات در فایل {self.config_file} ذخیره شد")
            
        except Exception as e:
            logger.error(f"خطا در ذخیره تنظیمات: {str(e)}")
            raise
            
    def get(self, key: str, default: Any = None) -> Any:
        """دریافت مقدار تنظیمات"""
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                value = value[k]
                
            return value
            
        except (KeyError, TypeError):
            return default
            
    def set(self, key: str, value: Any) -> None:
        """تنظیم مقدار تنظیمات"""
        try:
            keys = key.split('.')
            config = self.config
            
            # پیدا کردن آخرین کلید
            for k in keys[:-1]:
                config = config[k]
                
            # تنظیم مقدار
            config[keys[-1]] = value
            
            # ذخیره تغییرات
            self.save_config()
            
        except Exception as e:
            logger.error(f"خطا در تنظیم مقدار {key}: {str(e)}")
            raise
            
    def __getitem__(self, key: str) -> Any:
        """پشتیبانی از دسترسی با براکت"""
        return self.get(key)
        
    def __setitem__(self, key: str, value: Any) -> None:
        """پشتیبانی از تنظیم با براکت"""
        self.set(key, value)
        
    def __contains__(self, key: str) -> bool:
        """پشتیبانی از عملگر in"""
        try:
            self.get(key)
            return True
        except (KeyError, TypeError):
            return False 