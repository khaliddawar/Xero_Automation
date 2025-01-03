import requests
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class CurrencyConverter:
    def __init__(self):
        self.base_currency = 'BHD'
        self.rates_cache = {}
        self.cache_timestamp = None
        self.cache_duration = 24 * 60 * 60  # 24 hours in seconds

    def get_exchange_rate(self, from_currency: str, to_currency: str = 'BHD') -> Optional[float]:
        """Get exchange rate with caching"""
        try:
            # Check cache first
            cache_key = f"{from_currency}_{to_currency}"
            if self._is_cache_valid() and cache_key in self.rates_cache:
                return self.rates_cache[cache_key]

            # SAR to BHD fixed rate
            if from_currency == 'SAR' and to_currency == 'BHD':
                rate = 0.099  # Fixed rate: 1 SAR = 0.099 BHD
                self.rates_cache[cache_key] = rate
                self.cache_timestamp = datetime.now().timestamp()
                return rate

            # For other currencies, you could add an API call here
            # Example with exchangerate-api.com:
            # api_key = "your_api_key"
            # response = requests.get(f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}")
            # rate = response.json()['conversion_rate']

            return None

        except Exception as e:
            logger.error(f"Error getting exchange rate: {str(e)}")
            return None

    def convert_amount(self, amount: float, from_currency: str, to_currency: str = 'BHD') -> Optional[float]:
        """Convert amount between currencies"""
        try:
            if from_currency == to_currency:
                return amount

            rate = self.get_exchange_rate(from_currency, to_currency)
            if not rate:
                raise ValueError(f"Could not get exchange rate for {from_currency} to {to_currency}")

            converted = round(amount * rate, 3)  # BHD uses 3 decimal places
            logger.info(f"Converted {amount} {from_currency} to {converted} {to_currency}")
            return converted

        except Exception as e:
            logger.error(f"Error converting amount: {str(e)}")
            return None

    def _is_cache_valid(self) -> bool:
        """Check if cached rates are still valid"""
        if not self.cache_timestamp:
            return False
        
        current_time = datetime.now().timestamp()
        return (current_time - self.cache_timestamp) < self.cache_duration