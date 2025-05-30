#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ماژول پیش‌بینی قند خون با استفاده از هوش مصنوعی
"""

import logging
from datetime import datetime, timedelta
import numpy as np
from .analyzer import AIAnalyzer

class AIPredictor:
    """
    کلاس پیش‌بینی‌کننده قند خون با استفاده از هوش مصنوعی پیشرفته‌تر
    """
    def __init__(self):
        self.analyzer = AIAnalyzer()
        self.is_trained = False
        self.prediction_horizon = 24  # پیش‌بینی تا 24 ساعت آینده

    def train(self, readings):
        """
        آموزش مدل پیش‌بینی با استفاده از داده‌های قند خون
        """
        try:
            if len(readings) < 15:  # نیاز به داده‌های بیشتر برای پیش‌بینی پیشرفته
                return False
            
            # استفاده از آنالایزر پایه برای آموزش اولیه
            base_training = self.analyzer.train_model(readings)
            if not base_training:
                return False
            
            # آموزش مدل پیشرفته‌تر (در نسخه‌های آینده)
            self.is_trained = True
            return True
            
        except Exception as e:
            logging.error(f"خطا در آموزش مدل پیش‌بینی: {e}")
            return False

    def predict_next_day(self, user_id=1):
        """
        پیش‌بینی قند خون برای 24 ساعت آینده
        """
        try:
            if not self.is_trained:
                return None
            
            predictions = []
            confidence_scores = []
            
            # پیش‌بینی برای هر ساعت
            for hour in range(24):
                glucose, confidence = self.analyzer.predict_glucose(hour)
                if glucose is not None:
                    predictions.append({
                        'hour': hour,
                        'glucose': glucose,
                        'confidence': confidence
                    })
                    confidence_scores.append(confidence)
            
            # میانگین اطمینان
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            return {
                'predictions': predictions,
                'avg_confidence': avg_confidence,
                'prediction_date': (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            }
            
        except Exception as e:
            logging.error(f"خطا در پیش‌بینی روز آینده: {e}")
            return None

    def get_critical_times(self, predictions, threshold_low=70, threshold_high=180):
        """
        شناسایی زمان‌های بحرانی در پیش‌بینی‌ها
        """
        try:
            if not predictions or 'predictions' not in predictions:
                return []
            
            critical_times = []
            
            for pred in predictions['predictions']:
                glucose = pred['glucose']
                hour = pred['hour']
                confidence = pred['confidence']
                
                if glucose < threshold_low and confidence > 0.5:
                    critical_times.append({
                        'hour': hour,
                        'glucose': glucose,
                        'type': 'low',
                        'message': f'احتمال افت قند در ساعت {hour}:00'
                    })
                elif glucose > threshold_high and confidence > 0.5:
                    critical_times.append({
                        'hour': hour,
                        'glucose': glucose,
                        'type': 'high',
                        'message': f'احتمال افزایش قند در ساعت {hour}:00'
                    })
            
            return critical_times
            
        except Exception as e:
            logging.error(f"خطا در شناسایی زمان‌های بحرانی: {e}")
            return []

    def generate_prediction_report(self, predictions):
        """
        تولید گزارش پیش‌بینی
        """
        try:
            if not predictions or 'predictions' not in predictions:
                return "داده‌ای برای گزارش وجود ندارد"
            
            report = f"گزارش پیش‌بینی قند خون برای تاریخ {predictions['prediction_date']}:\n\n"
            report += f"میانگین اطمینان پیش‌بینی: {predictions['avg_confidence']*100:.1f}%\n\n"
            
            # زمان‌های بحرانی
            critical_times = self.get_critical_times(predictions)
            if critical_times:
                report += "⚠️ هشدارهای پیش‌بینی شده:\n"
                for ct in critical_times:
                    report += f"• {ct['message']} - {ct['glucose']:.1f} mg/dL\n"
                report += "\n"
            
            # ساعات با بیشترین و کمترین قند
            all_glucose = [(p['hour'], p['glucose']) for p in predictions['predictions']]
            max_glucose = max(all_glucose, key=lambda x: x[1])
            min_glucose = min(all_glucose, key=lambda x: x[1])
            
            report += f"🔺 بیشترین قند پیش‌بینی شده: {max_glucose[1]:.1f} mg/dL در ساعت {max_glucose[0]}:00\n"
            report += f"🔻 کمترین قند پیش‌بینی شده: {min_glucose[1]:.1f} mg/dL در ساعت {min_glucose[0]}:00\n"
            
            report += "\n⚠️ توجه: این پیش‌بینی‌ها صرفاً جنبه آموزشی دارند و نباید جایگزین مشاوره پزشکی شوند."
            
            return report
            
        except Exception as e:
            logging.error(f"خطا در تولید گزارش پیش‌بینی: {e}")
            return "خطا در تولید گزارش"