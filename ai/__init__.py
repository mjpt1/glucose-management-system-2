# این فایل برای شناسایی پوشه ai به عنوان یک پکیج پایتون است

from .analyzer import AIAnalyzer
from .predictor import AIPredictor
from .food_recognition import FoodRecognizer

__all__ = ['AIAnalyzer', 'AIPredictor', 'FoodRecognizer']