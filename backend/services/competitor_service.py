import requests
import random
import logging
from datetime import datetime, timedelta
import json

class CompetitorService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mock_api_url = "https://mock-api.com/competitor-prices"
        self.cache = {}
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
    
    def get_competitor_price(self, product_id):
        """
        Get competitor price for a product
        First tries real API, falls back to mock data
        """
        try:
            # Check cache first
            if self._is_cached(product_id):
                return self.cache[product_id]['price']
            
            # Try to fetch from real API (will likely fail, that's expected)
            competitor_price = self._fetch_from_api(product_id)
            
            if competitor_price is None:
                # Fall back to mock data
                competitor_price = self._generate_mock_price(product_id)
            
            # Cache the result
            self._cache_price(product_id, competitor_price)
            
            return competitor_price
            
        except Exception as e:
            self.logger.error(f"Error getting competitor price for {product_id}: {str(e)}")
            return self._generate_mock_price(product_id)
    
    def get_competitor_prices_bulk(self, product_ids):
        """
        Get competitor prices for multiple products
        """
        try:
            # Try bulk API call first
            bulk_data = self._fetch_bulk_from_api(product_ids)
            
            if bulk_data:
                # Cache all results
                for item in bulk_data:
                    self._cache_price(item['product_id'], item['competitor_price'])
                
                return {item['product_id']: item['competitor_price'] for item in bulk_data}
            
            # Fall back to individual mock prices
            result = {}
            for product_id in product_ids:
                result[product_id] = self.get_competitor_price(product_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting bulk competitor prices: {str(e)}")
            return {pid: self._generate_mock_price(pid) for pid in product_ids}
    
    def _fetch_from_api(self, product_id):
        """
        Try to fetch from real competitor API
        """
        try:
            # This will likely fail since the API doesn't exist
            response = requests.get(
                f"{self.mock_api_url}/{product_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('competitor_price')
                
        except Exception as e:
            self.logger.debug(f"API call failed (expected): {str(e)}")
            
        return None
    
    def _fetch_bulk_from_api(self, product_ids):
        """
        Try to fetch bulk data from competitor API
        """
        try:
            response = requests.post(
                self.mock_api_url,
                json={'product_ids': product_ids},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
                
        except Exception as e:
            self.logger.debug(f"Bulk API call failed (expected): {str(e)}")
            
        return None
    
    def _generate_mock_price(self, product_id):
        """
        Generate realistic mock competitor prices
        """
        # Use product_id as seed for consistent mock data
        random.seed(hash(product_id) % (2**32))
        
        # Base price categories
        price_ranges = {
            'P001': (80, 120),    # Electronics
            'P002': (150, 250),   # Apparel  
            'P003': (40, 65),     # Home
        }
        
        # Get base range or use default
        if product_id in price_ranges:
            min_price, max_price = price_ranges[product_id]
        else:
            # Generate based on product_id pattern
            if product_id.startswith('P00'):
                # Extract number from product ID
                try:
                    num = int(product_id[3:])
                    if num <= 100:
                        min_price, max_price = (50, 150)
                    elif num <= 500:
                        min_price, max_price = (100, 300)
                    else:
                        min_price, max_price = (20, 80)
                except:
                    min_price, max_price = (50, 150)
            else:
                min_price, max_price = (50, 150)
        
        # Add some randomness
        price_variation = random.uniform(-0.2, 0.2)  # ±20% variation
        base_price = random.uniform(min_price, max_price)
        final_price = base_price * (1 + price_variation)
        
        # Add market trend simulation
        trend_factor = self._get_market_trend_factor()
        final_price *= trend_factor
        
        return round(final_price, 2)
    
    def _get_market_trend_factor(self):
        """
        Simulate market trends affecting competitor prices
        """
        # Simulate different market conditions
        market_conditions = [
            0.95,  # Market downturn
            0.98,  # Slight decrease
            1.0,   # Stable
            1.02,  # Slight increase  
            1.05   # Market upturn
        ]
        
        # Use current time to simulate changing conditions
        time_seed = int(datetime.now().timestamp()) // 3600  # Changes every hour
        random.seed(time_seed)
        
        return random.choice(market_conditions)
    
    def _is_cached(self, product_id):
        """
        Check if price is cached and still valid
        """
        if product_id not in self.cache:
            return False
        
        cached_time = self.cache[product_id]['timestamp']
        return datetime.now() - cached_time < self.cache_duration
    
    def _cache_price(self, product_id, price):
        """
        Cache competitor price
        """
        self.cache[product_id] = {
            'price': price,
            'timestamp': datetime.now()
        }
    
    def get_market_analysis(self, our_products):
        """
        Analyze market position relative to competitors
        """
        try:
            analysis = {
                'total_products': len(our_products),
                'competitive_position': {
                    'higher_priced': 0,
                    'lower_priced': 0,
                    'similar_priced': 0
                },
                'price_differences': [],
                'recommendations': []
            }
            
            for product in our_products:
                competitor_price = self.get_competitor_price(product.id)
                if competitor_price:
                    price_diff = product.current_price - competitor_price
                    price_diff_percent = (price_diff / competitor_price) * 100
                    
                    analysis['price_differences'].append({
                        'product_id': product.id,
                        'our_price': product.current_price,
                        'competitor_price': competitor_price,
                        'difference': price_diff,
                        'difference_percent': round(price_diff_percent, 2)
                    })
                    
                    # Categorize position
                    if price_diff_percent > 5:
                        analysis['competitive_position']['higher_priced'] += 1
                    elif price_diff_percent < -5:
                        analysis['competitive_position']['lower_priced'] += 1
                    else:
                        analysis['competitive_position']['similar_priced'] += 1
                    
                    # Generate recommendations
                    if price_diff_percent > 20:
                        analysis['recommendations'].append({
                            'product_id': product.id,
                            'type': 'price_reduction',
                            'message': f'Consider reducing price - {price_diff_percent:.1f}% above competitor',
                            'priority': 'high'
                        })
                    elif price_diff_percent < -15:
                        analysis['recommendations'].append({
                            'product_id': product.id,
                            'type': 'price_increase',
                            'message': f'Opportunity to increase price - {abs(price_diff_percent):.1f}% below competitor',
                            'priority': 'medium'
                        })
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in market analysis: {str(e)}")
            return {'error': str(e)}
    
    def simulate_competitor_price_change(self, product_id, change_percent):
        """
        Simulate a competitor price change (for testing)
        """
        current_price = self.get_competitor_price(product_id)
        new_price = current_price * (1 + change_percent / 100)
        
        # Update cache with new price
        self._cache_price(product_id, round(new_price, 2))
        
        return {
            'product_id': product_id,
            'old_price': current_price,
            'new_price': round(new_price, 2),
            'change_percent': change_percent
        }
    
    def get_price_history_simulation(self, product_id, days=30):
        """
        Generate simulated competitor price history
        """
        try:
            current_price = self.get_competitor_price(product_id)
            history = []
            
            # Generate price history with realistic fluctuations
            for i in range(days):
                date = datetime.now().date() - timedelta(days=days-i)
                
                # Simulate price variations
                daily_variation = random.uniform(-0.03, 0.03)  # ±3% daily variation
                if i == 0:
                    price = current_price
                else:
                    price = history[-1]['price'] * (1 + daily_variation)
                
                # Ensure price doesn't go too extreme
                price = max(current_price * 0.8, min(current_price * 1.2, price))
                
                history.append({
                    'date': date.isoformat(),
                    'price': round(price, 2)
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error generating price history for {product_id}: {str(e)}")
            return []
    
    def clear_cache(self):
        """
        Clear competitor price cache
        """
        self.cache = {}
        self.logger.info("Competitor price cache cleared")
    
    def get_cache_stats(self):
        """
        Get cache statistics
        """
        valid_entries = sum(1 for pid in self.cache if self._is_cached(pid))
        
        return {
            'total_entries': len(self.cache),
            'valid_entries': valid_entries,
            'expired_entries': len(self.cache) - valid_entries,
            'cache_duration_hours': self.cache_duration.total_seconds() / 3600
        }

    def fetch_competitor_prices(self):
        """
        Return mock competitor prices for all products (local mock, not from external API)
        """
        return [
            {"product_id": "P001", "competitor_price": 90.0},
            {"product_id": "P002", "competitor_price": 195.0},
            {"product_id": "P003", "competitor_price": 48.0},
            {"product_id": "P004", "competitor_price": 140.0},
            {"product_id": "P005", "competitor_price": 280.0},
            {"product_id": "P006", "competitor_price": 110.0},
            {"product_id": "P007", "competitor_price": 40.0},
            {"product_id": "P008", "competitor_price": 75.0},
            {"product_id": "P009", "competitor_price": 170.0},
            {"product_id": "P010", "competitor_price": 210.0},
        ] 