#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مدیریت کاربران سیستم
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self, db_manager):
        """مقداردهی اولیه مدیریت کاربران"""
        self.db = db_manager
        
    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """ایجاد کاربر جدید"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users 
                    (name, age, weight, height, diabetes_type, target_min, target_max)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_data['name'],
                    user_data.get('age', 30),
                    user_data.get('weight', 70.0),
                    user_data.get('height', 170.0),
                    user_data.get('diabetes_type', 'نوع 2'),
                    user_data.get('target_min', 80),
                    user_data.get('target_max', 140)
                ))
                conn.commit()
                logger.info(f"کاربر جدید با نام {user_data['name']} ایجاد شد")
                return True
        except Exception as e:
            logger.error(f"خطا در ایجاد کاربر: {str(e)}")
            return False
            
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """دریافت اطلاعات کاربر"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
                user = cursor.fetchone()
                if user:
                    return {
                        'id': user[0],
                        'name': user[1],
                        'age': user[2],
                        'weight': user[3],
                        'height': user[4],
                        'diabetes_type': user[5],
                        'target_min': user[6],
                        'target_max': user[7],
                        'created_at': user[8],
                        'updated_at': user[9]
                    }
                return None
        except Exception as e:
            logger.error(f"خطا در دریافت اطلاعات کاربر: {str(e)}")
            return None
            
    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> bool:
        """به‌روزرسانی اطلاعات کاربر"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                update_fields = []
                values = []
                for key, value in user_data.items():
                    if key != 'id':
                        update_fields.append(f"{key} = ?")
                        values.append(value)
                values.append(user_id)
                
                cursor.execute(f'''
                    UPDATE users 
                    SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', values)
                conn.commit()
                logger.info(f"اطلاعات کاربر {user_id} با موفقیت به‌روزرسانی شد")
                return True
        except Exception as e:
            logger.error(f"خطا در به‌روزرسانی اطلاعات کاربر: {str(e)}")
            return False
            
    def delete_user(self, user_id: int) -> bool:
        """حذف کاربر"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                # حذف خوانش‌های کاربر
                cursor.execute('DELETE FROM readings WHERE user_id = ?', (user_id,))
                # حذف یادآوری‌های کاربر
                cursor.execute('DELETE FROM reminders WHERE user_id = ?', (user_id,))
                # حذف پیش‌بینی‌های کاربر
                cursor.execute('DELETE FROM predictions WHERE user_id = ?', (user_id,))
                # حذف وعده‌های غذایی کاربر
                cursor.execute('DELETE FROM meals WHERE user_id = ?', (user_id,))
                # حذف کاربر
                cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
                conn.commit()
                logger.info(f"کاربر {user_id} و تمام داده‌های مرتبط با موفقیت حذف شد")
                return True
        except Exception as e:
            logger.error(f"خطا در حذف کاربر: {str(e)}")
            return False
            
    def get_all_users(self) -> List[Dict[str, Any]]:
        """دریافت لیست تمام کاربران"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users ORDER BY name')
                users = []
                for user in cursor.fetchall():
                    users.append({
                        'id': user[0],
                        'name': user[1],
                        'age': user[2],
                        'weight': user[3],
                        'height': user[4],
                        'diabetes_type': user[5],
                        'target_min': user[6],
                        'target_max': user[7],
                        'created_at': user[8],
                        'updated_at': user[9]
                    })
                return users
        except Exception as e:
            logger.error(f"خطا در دریافت لیست کاربران: {str(e)}")
            return []
            
    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """دریافت آمار کاربر"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # تعداد خوانش‌ها
                cursor.execute('SELECT COUNT(*) FROM readings WHERE user_id = ?', (user_id,))
                total_readings = cursor.fetchone()[0]
                
                # میانگین قند خون
                cursor.execute('SELECT AVG(glucose_level) FROM readings WHERE user_id = ?', (user_id,))
                avg_glucose = cursor.fetchone()[0] or 0
                
                # تعداد یادآوری‌های فعال
                cursor.execute('SELECT COUNT(*) FROM reminders WHERE user_id = ? AND is_active = 1', (user_id,))
                active_reminders = cursor.fetchone()[0]
                
                # تعداد وعده‌های غذایی
                cursor.execute('SELECT COUNT(*) FROM meals WHERE user_id = ?', (user_id,))
                total_meals = cursor.fetchone()[0]
                
                return {
                    'total_readings': total_readings,
                    'avg_glucose': round(avg_glucose, 1),
                    'active_reminders': active_reminders,
                    'total_meals': total_meals
                }
        except Exception as e:
            logger.error(f"خطا در دریافت آمار کاربر: {str(e)}")
            return {
                'total_readings': 0,
                'avg_glucose': 0,
                'active_reminders': 0,
                'total_meals': 0
            } 