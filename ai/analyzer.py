#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ماژول تحلیل داده‌های قند خون با استفاده از هوش مصنوعی
"""

import logging
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib
import os

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """
    کلاس تحلیل‌گر هوش مصنوعی برای تحلیل داده‌های قند خون
    """
    def __init__(self, db_manager, config):
        """مقداردهی اولیه تحلیلگر"""
        self.db = db_manager
        self.config = config
        self.model_path = os.path.join('models', 'glucose_predictor.joblib')
        self.scaler_path = os.path.join('models', 'scaler.joblib')
        
        # بارگذاری یا ایجاد مدل
        self._load_or_create_model()
        
    def _load_or_create_model(self):
        """بارگذاری یا ایجاد مدل پیش‌بینی"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                logger.info("مدل پیش‌بینی با موفقیت بارگذاری شد")
            else:
                self.model = LinearRegression()
                self.scaler = StandardScaler()
                logger.info("مدل پیش‌بینی جدید ایجاد شد")
        except Exception as e:
            logger.error(f"خطا در بارگذاری/ایجاد مدل: {str(e)}")
            raise
            
    def _prepare_data(self, readings):
        """آماده‌سازی داده‌ها برای آموزش مدل"""
        try:
            # تبدیل داده‌ها به آرایه numpy
            X = np.array([[r['value']] for r in readings[:-1]])  # مقادیر قبلی
            y = np.array([r['value'] for r in readings[1:]])     # مقادیر بعدی
            
            # نرمال‌سازی داده‌ها
            X = self.scaler.fit_transform(X)
            
            return X, y
            
        except Exception as e:
            logger.error(f"خطا در آماده‌سازی داده‌ها: {str(e)}")
            raise
            
    def train_model(self):
        """آموزش مدل با داده‌های جدید"""
        try:
            # دریافت داده‌های آموزشی
            readings = self.db.get_glucose_readings(limit=100)  # 100 خوانش آخر
            
            if len(readings) < 2:
                logger.warning("داده‌های کافی برای آموزش مدل وجود ندارد")
                return False
                
            # آماده‌سازی داده‌ها
            X, y = self._prepare_data(readings)
            
            # آموزش مدل
            self.model.fit(X, y)
            
            # ذخیره مدل
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            
            logger.info("مدل با موفقیت آموزش داده شد")
            return True
            
        except Exception as e:
            logger.error(f"خطا در آموزش مدل: {str(e)}")
            return False
            
    def predict_next_reading(self, current_value):
        """پیش‌بینی مقدار قند خون بعدی"""
        try:
            # نرمال‌سازی مقدار فعلی
            X = self.scaler.transform([[current_value]])
            
            # پیش‌بینی
            prediction = self.model.predict(X)[0]
            
            return round(prediction, 1)
            
        except Exception as e:
            logger.error(f"خطا در پیش‌بینی: {str(e)}")
            return None
            
    def analyze_trends(self, readings):
        """تحلیل روند قند خون"""
        try:
            if not readings:
                return None
                
            values = [r['value'] for r in readings]
            
            # محاسبه میانگین
            mean = np.mean(values)
            
            # محاسبه انحراف معیار
            std = np.std(values)
            
            # محاسبه روند (شیب خط رگرسیون)
            x = np.arange(len(values))
            slope = np.polyfit(x, values, 1)[0]
            
            # تعیین وضعیت روند
            if slope > 0.5:
                trend = "صعودی"
            elif slope < -0.5:
                trend = "نزولی"
            else:
                trend = "ثابت"
                
            return {
                'mean': round(mean, 1),
                'std': round(std, 1),
                'trend': trend,
                'slope': round(slope, 2)
            }
            
        except Exception as e:
            logger.error(f"خطا در تحلیل روند: {str(e)}")
            return None
            
    def get_recommendations(self, readings):
        """دریافت توصیه‌های هوشمند"""
        try:
            if not readings:
                return []
                
            recommendations = []
            analysis = self.analyze_trends(readings)
            
            if analysis:
                # توصیه بر اساس روند
                if analysis['trend'] == "صعودی":
                    recommendations.append("روند قند خون شما صعودی است. لطفاً با پزشک خود مشورت کنید.")
                elif analysis['trend'] == "نزولی":
                    recommendations.append("روند قند خون شما نزولی است. مراقب افت قند خون باشید.")
                    
                # توصیه بر اساس انحراف معیار
                if analysis['std'] > 30:
                    recommendations.append("تغییرات قند خون شما زیاد است. سعی کنید رژیم غذایی خود را منظم‌تر کنید.")
                    
                # توصیه بر اساس میانگین
                if analysis['mean'] > 180:
                    recommendations.append("میانگین قند خون شما بالاست. رژیم غذایی و فعالیت بدنی خود را بررسی کنید.")
                elif analysis['mean'] < 70:
                    recommendations.append("میانگین قند خون شما پایین است. با پزشک خود مشورت کنید.")
                    
            return recommendations
            
        except Exception as e:
            logger.error(f"خطا در دریافت توصیه‌ها: {str(e)}")
            return []

    def analyze_patterns(self, readings):
        """تحلیل الگوها"""
        try:
            if len(readings) < 5:
                return "داده کافی برای تحلیل وجود ندارد"
            
            glucose_levels = [r[5] for r in readings]
            avg_glucose = sum(glucose_levels) / len(glucose_levels)
            
            analysis = f"میانگین قند خون: {avg_glucose:.1f} mg/dL\n"
            
            if avg_glucose < 80:
                analysis += "⚠️ میانگین قند خون پایین است\n"
            elif avg_glucose > 140:
                analysis += "⚠️ میانگین قند خون بالا است\n"
            else:
                analysis += "✅ میانگین قند خون در محدوده مطلوب است\n"
            
            # تحلیل روند
            recent_avg = sum(glucose_levels[:5]) / min(5, len(glucose_levels))
            older_avg = sum(glucose_levels[-5:]) / min(5, len(glucose_levels))
            
            if recent_avg > older_avg + 10:
                analysis += "📈 روند افزایشی قند خون\n"
            elif recent_avg < older_avg - 10:
                analysis += "📉 روند کاهشی قند خون\n"
            else:
                analysis += "➡️ روند ثابت قند خون\n"
            
            return analysis
            
        except Exception as e:
            logging.error(f"خطا در تحلیل الگوها: {e}")
            return "خطا در تحلیل"