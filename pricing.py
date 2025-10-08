# pricing.py
from abc import ABC, abstractmethod

class PricingStrategy(ABC):
    @abstractmethod
    def calculate(self, duration: int) -> float:
        """Calculate parking fee given duration in seconds"""
        pass

class FlatRate(PricingStrategy):
    def calculate(self, duration: int) -> float:
        return 50.0  # Flat fee

class HourlyRate(PricingStrategy):
    def calculate(self, duration: int) -> float:
        hours = (duration // 3600) + 1
        return hours * 50.0

class PerMinute(PricingStrategy):
    def calculate(self, duration: int) -> float:
        minutes = (duration // 60) + 1
        return minutes * 10.0