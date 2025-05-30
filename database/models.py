# -*- coding: utf-8 -*-
# مدل‌های پایگاه داده برای سیستم مدیریت قند خون

class User:
    """کلاس کاربر برای ذخیره اطلاعات کاربران"""
    def __init__(self, id=None, username=None, age=None, gender=None, target_glucose_min=None, target_glucose_max=None):
        self.id = id
        self.username = username
        self.age = age
        self.gender = gender
        self.target_glucose_min = target_glucose_min
        self.target_glucose_max = target_glucose_max

    def to_dict(self):
        """تبدیل اطلاعات کاربر به دیکشنری"""
        return {
            'id': self.id,
            'username': self.username,
            'age': self.age,
            'gender': self.gender,
            'target_glucose_min': self.target_glucose_min,
            'target_glucose_max': self.target_glucose_max
        }

    @classmethod
    def from_dict(cls, data):
        """ساخت شیء کاربر از دیکشنری"""
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            age=data.get('age'),
            gender=data.get('gender'),
            target_glucose_min=data.get('target_glucose_min'),
            target_glucose_max=data.get('target_glucose_max')
        )


class Reading:
    """کلاس خوانش قند خون"""
    def __init__(self, id=None, user_id=None, glucose_level=None, date=None, time=None, description=None):
        self.id = id
        self.user_id = user_id
        self.glucose_level = glucose_level
        self.date = date
        self.time = time
        self.description = description

    def to_dict(self):
        """تبدیل اطلاعات خوانش به دیکشنری"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'glucose_level': self.glucose_level,
            'date': self.date,
            'time': self.time,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data):
        """ساخت شیء خوانش از دیکشنری"""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            glucose_level=data.get('glucose_level'),
            date=data.get('date'),
            time=data.get('time'),
            description=data.get('description')
        )


class Reminder:
    """کلاس یادآور"""
    def __init__(self, id=None, user_id=None, title=None, time=None, message=None, is_active=True):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.time = time
        self.message = message
        self.is_active = is_active

    def to_dict(self):
        """تبدیل اطلاعات یادآور به دیکشنری"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'time': self.time,
            'message': self.message,
            'is_active': self.is_active
        }

    @classmethod
    def from_dict(cls, data):
        """ساخت شیء یادآور از دیکشنری"""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            title=data.get('title'),
            time=data.get('time'),
            message=data.get('message'),
            is_active=data.get('is_active', True)
        )


class Prediction:
    """کلاس پیش‌بینی قند خون"""
    def __init__(self, id=None, user_id=None, predicted_level=None, time=None, confidence=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.predicted_level = predicted_level
        self.time = time
        self.confidence = confidence
        self.created_at = created_at

    def to_dict(self):
        """تبدیل اطلاعات پیش‌بینی به دیکشنری"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'predicted_level': self.predicted_level,
            'time': self.time,
            'confidence': self.confidence,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        """ساخت شیء پیش‌بینی از دیکشنری"""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            predicted_level=data.get('predicted_level'),
            time=data.get('time'),
            confidence=data.get('confidence'),
            created_at=data.get('created_at')
        )