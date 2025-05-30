#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ماژول تشخیص غذا با استفاده از هوش مصنوعی
"""

import logging
import os
import json
import numpy as np

class FoodRecognizer:
    """
    کلاس تشخیص غذا با استفاده از هوش مصنوعی
    این کلاس برای تشخیص نوع غذا از روی تصویر و تخمین کربوهیدرات آن استفاده می‌شود
    """
    def __init__(self, model_path=None, labels_path=None):
        self.model = None
        self.labels = {}
        self.is_loaded = False
        self.model_path = model_path
        self.labels_path = labels_path
        self.food_carbs_db = {
            # دیکشنری پایه برای کربوهیدرات غذاهای رایج (گرم کربوهیدرات در 100 گرم غذا)
            'نان': 50,
            'برنج': 28,
            'سیب‌زمینی': 17,
            'ماکارونی': 25,
            'سیب': 14,
            'موز': 23,
            'پرتقال': 12,
            'شیر': 5,
            'ماست': 4,
            'گوشت': 0,
            'مرغ': 0,
            'ماهی': 0,
            'تخم‌مرغ': 1,
            'عدس': 20,
            'لوبیا': 19,
            'نخود': 21,
            'شکلات': 55,
            'کیک': 50,
            'بیسکویت': 70,
            'آبمیوه': 10,
            'نوشابه': 11
        }

    def load_model(self):
        """
        بارگذاری مدل تشخیص غذا
        """
        try:
            # در نسخه واقعی، اینجا باید مدل یادگیری عمیق بارگذاری شود
            # برای مثال با استفاده از TensorFlow یا PyTorch
            
            # شبیه‌سازی بارگذاری مدل
            if self.model_path and os.path.exists(self.model_path):
                logging.info(f"بارگذاری مدل از {self.model_path}")
                # self.model = tf.keras.models.load_model(self.model_path)
                self.model = "شبیه‌سازی مدل تشخیص غذا"
            else:
                logging.warning("مسیر مدل نامعتبر است - استفاده از مدل پیش‌فرض")
                self.model = "شبیه‌سازی مدل تشخیص غذا"
            
            # بارگذاری برچسب‌ها
            if self.labels_path and os.path.exists(self.labels_path):
                with open(self.labels_path, 'r', encoding='utf-8') as f:
                    self.labels = json.load(f)
            
            self.is_loaded = True
            return True
            
        except Exception as e:
            logging.error(f"خطا در بارگذاری مدل تشخیص غذا: {e}")
            return False

    def recognize_food(self, image_path):
        """
        تشخیص نوع غذا از روی تصویر
        """
        try:
            if not self.is_loaded:
                success = self.load_model()
                if not success:
                    return None, 0.0
            
            # در نسخه واقعی، اینجا باید تصویر پردازش و به مدل داده شود
            # برای مثال:
            # image = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
            # image_array = tf.keras.preprocessing.image.img_to_array(image)
            # image_array = np.expand_dims(image_array, axis=0)
            # image_array = image_array / 255.0  # نرمال‌سازی
            # predictions = self.model.predict(image_array)
            # predicted_class = np.argmax(predictions[0])
            # confidence = predictions[0][predicted_class]
            # food_name = self.labels.get(str(predicted_class), "ناشناخته")
            
            # شبیه‌سازی تشخیص غذا
            # در نسخه واقعی، این قسمت با کد بالا جایگزین می‌شود
            import random
            foods = list(self.food_carbs_db.keys())
            food_name = random.choice(foods)
            confidence = random.uniform(0.7, 0.95)
            
            return food_name, confidence
            
        except Exception as e:
            logging.error(f"خطا در تشخیص غذا: {e}")
            return None, 0.0

    def estimate_carbs(self, food_name, portion_size=100):
        """
        تخمین میزان کربوهیدرات غذا
        
        پارامترها:
        food_name -- نام غذا
        portion_size -- اندازه پرس به گرم (پیش‌فرض: 100 گرم)
        
        خروجی:
        میزان کربوهیدرات به گرم
        """
        try:
            # جستجو در پایگاه داده کربوهیدرات
            carbs_per_100g = self.food_carbs_db.get(food_name, None)
            
            if carbs_per_100g is None:
                # اگر غذا در پایگاه داده نباشد، مقدار پیش‌فرض برگردانده می‌شود
                logging.warning(f"اطلاعات کربوهیدرات برای {food_name} یافت نشد")
                return 15  # مقدار پیش‌فرض
            
            # محاسبه کربوهیدرات بر اساس اندازه پرس
            carbs = (carbs_per_100g * portion_size) / 100
            
            return carbs
            
        except Exception as e:
            logging.error(f"خطا در تخمین کربوهیدرات: {e}")
            return 15  # مقدار پیش‌فرض در صورت خطا

    def analyze_meal(self, image_path, portion_size=100):
        """
        تحلیل کامل وعده غذایی
        
        پارامترها:
        image_path -- مسیر تصویر غذا
        portion_size -- اندازه پرس به گرم (پیش‌فرض: 100 گرم)
        
        خروجی:
        دیکشنری حاوی اطلاعات تحلیل
        """
        try:
            food_name, confidence = self.recognize_food(image_path)
            
            if not food_name:
                return {
                    'success': False,
                    'message': 'خطا در تشخیص غذا'
                }
            
            carbs = self.estimate_carbs(food_name, portion_size)
            
            # تخمین تأثیر بر قند خون
            glucose_impact = 'کم'
            if carbs > 30:
                glucose_impact = 'زیاد'
            elif carbs > 15:
                glucose_impact = 'متوسط'
            
            return {
                'success': True,
                'food_name': food_name,
                'confidence': confidence,
                'carbs': carbs,
                'portion_size': portion_size,
                'glucose_impact': glucose_impact,
                'message': f"غذای شناسایی شده: {food_name} (اطمینان: {confidence*100:.1f}%)\n"
                          f"میزان کربوهیدرات: {carbs:.1f} گرم\n"
                          f"تأثیر بر قند خون: {glucose_impact}"
            }
            
        except Exception as e:
            logging.error(f"خطا در تحلیل وعده غذایی: {e}")
            return {
                'success': False,
                'message': f'خطا در تحلیل: {str(e)}'
            }