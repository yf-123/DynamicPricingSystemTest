from app import db
from models.product import Product
from models.pricing_history import PricingHistory
from datetime import datetime
import logging

class PricingService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def optimize_price(self, product, ml_prediction, competitor_price=None):
        """
        Apply dynamic pricing optimization with business rules
        """
        try:
            old_price = product.current_price
            suggested_price = ml_prediction
            adjustment_reasons = []
            adjustment_type = 'AI_PREDICTION'
            
            # Business Rule 1: Low inventory adjustment
            if product.is_low_inventory(threshold=10):
                # Increase price by up to 30% for low inventory
                inventory_adjustment = min(0.30, (10 - product.inventory) * 0.05)
                suggested_price = suggested_price * (1 + inventory_adjustment)
                adjustment_reasons.append(f"Low inventory adjustment: +{inventory_adjustment*100:.1f}%")
                adjustment_type = 'INVENTORY_LOW'
            
            # Business Rule 2: Competitor pricing adjustment
            if competitor_price:
                price_difference_percent = ((suggested_price - competitor_price) / competitor_price) * 100
                
                # If we're significantly higher than competitor (>15%), reduce price
                if price_difference_percent > 15:
                    # Reduce price by up to 20%, ensuring minimum profit margins
                    competitor_adjustment = min(0.20, (price_difference_percent - 15) * 0.01)
                    suggested_price = suggested_price * (1 - competitor_adjustment)
                    adjustment_reasons.append(f"Competitor price adjustment: -{competitor_adjustment*100:.1f}%")
                    adjustment_type = 'COMPETITOR_PRICE'
            
            # Business Rule 3: Ensure price bounds
            min_price = product.get_min_price()  # cost + 10%
            max_price = product.get_max_price()  # base price + 50%
            
            original_suggested = suggested_price
            if suggested_price < min_price:
                suggested_price = min_price
                adjustment_reasons.append(f"Minimum price constraint applied: ${min_price:.2f}")
            elif suggested_price > max_price:
                suggested_price = max_price
                adjustment_reasons.append(f"Maximum price constraint applied: ${max_price:.2f}")
            
            # Update product price
            final_price = product.update_price(suggested_price)
            
            # Record pricing history
            pricing_history = PricingHistory(
                product_id=product.id,
                old_price=old_price,
                new_price=final_price,
                adjustment_reason='; '.join(adjustment_reasons) if adjustment_reasons else 'AI price optimization',
                adjustment_type=adjustment_type
            )
            
            db.session.add(pricing_history)
            db.session.commit()
            
            # Calculate impact metrics
            price_change_percent = ((final_price - old_price) / old_price) * 100
            profit_margin = product.get_profit_margin()
            
            return {
                'success': True,
                'product_id': product.id,
                'old_price': old_price,
                'new_price': final_price,
                'ml_prediction': ml_prediction,
                'competitor_price': competitor_price,
                'price_change_percent': round(price_change_percent, 2),
                'profit_margin': round(profit_margin, 2),
                'adjustment_reasons': adjustment_reasons,
                'adjustment_type': adjustment_type,
                'constraints_applied': original_suggested != final_price
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing price for product {product.id}: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'product_id': product.id,
                'error': str(e)
            }
    
    def calculate_demand_elasticity(self, product):
        """
        Calculate price elasticity of demand for a product
        """
        try:
            # Get recent pricing history
            price_changes = PricingHistory.query.filter_by(product_id=product.id)\
                .order_by(PricingHistory.timestamp.desc()).limit(5).all()
            
            if len(price_changes) < 2:
                return None
            
            # Simple elasticity calculation
            price_changes_data = []
            for i in range(len(price_changes) - 1):
                current = price_changes[i]
                previous = price_changes[i + 1]
                
                price_change = ((current.new_price - previous.new_price) / previous.new_price) * 100
                
                # This is simplified - in real implementation, you'd correlate with actual sales data
                # For now, we'll estimate based on inventory changes and sales patterns
                estimated_demand_change = self._estimate_demand_change(product, current, previous)
                
                if price_change != 0:
                    elasticity = estimated_demand_change / price_change
                    price_changes_data.append({
                        'price_change_percent': price_change,
                        'demand_change_percent': estimated_demand_change,
                        'elasticity': elasticity
                    })
            
            if price_changes_data:
                avg_elasticity = sum([pc['elasticity'] for pc in price_changes_data]) / len(price_changes_data)
                return {
                    'elasticity': round(avg_elasticity, 3),
                    'interpretation': 'elastic' if abs(avg_elasticity) > 1 else 'inelastic',
                    'price_sensitivity': 'high' if abs(avg_elasticity) > 1.5 else 'medium' if abs(avg_elasticity) > 0.5 else 'low'
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculating elasticity for product {product.id}: {str(e)}")
            return None
    
    def _estimate_demand_change(self, product, current_change, previous_change):
        """
        Estimate demand change based on available data
        This is a simplified estimation - in real implementation, 
        you'd use actual sales data correlation
        """
        # Use sales pattern and inventory changes as proxy for demand
        base_demand_change = 0
        
        # Factor in average rating impact
        if product.average_rating > 4.0:
            base_demand_change += 5  # High-rated products are less price sensitive
        elif product.average_rating < 3.0:
            base_demand_change -= 5  # Low-rated products are more price sensitive
        
        # Factor in category (some categories are more price sensitive)
        category_sensitivity = {
            'Electronics': -1.2,  # More price sensitive
            'Apparel': -0.8,
            'Home': -0.5,
            'Books': -1.5,
            'Luxury': -0.3  # Less price sensitive
        }
        
        category_factor = category_sensitivity.get(product.category, -1.0)
        base_demand_change += category_factor * 2
        
        return base_demand_change
    
    def get_pricing_recommendations(self, product):
        """
        Get pricing recommendations for a product
        """
        try:
            recommendations = []
            
            # Current status analysis
            current_margin = product.get_profit_margin()
            min_price = product.get_min_price()
            max_price = product.get_max_price()
            
            # Low inventory recommendation
            if product.is_low_inventory():
                recommended_increase = min(0.20, (10 - product.inventory) * 0.03)
                new_price = product.current_price * (1 + recommended_increase)
                if new_price <= max_price:
                    recommendations.append({
                        'type': 'inventory_adjustment',
                        'reason': f'Low inventory ({product.inventory} units)',
                        'current_price': product.current_price,
                        'recommended_price': round(new_price, 2),
                        'expected_impact': f'+{recommended_increase*100:.1f}% price increase',
                        'priority': 'high'
                    })
            
            # Profit margin optimization
            if current_margin < 20:  # Low profit margin
                target_margin = 25
                target_price = product.cost_price * (1 + target_margin / 100)
                if target_price <= max_price and target_price >= min_price:
                    recommendations.append({
                        'type': 'margin_optimization',
                        'reason': f'Low profit margin ({current_margin:.1f}%)',
                        'current_price': product.current_price,
                        'recommended_price': round(target_price, 2),
                        'expected_impact': f'Target {target_margin}% profit margin',
                        'priority': 'medium'
                    })
            
            # High inventory recommendation
            if product.inventory > 50:
                recommended_decrease = min(0.15, (product.inventory - 50) * 0.002)
                new_price = product.current_price * (1 - recommended_decrease)
                if new_price >= min_price:
                    recommendations.append({
                        'type': 'inventory_clearance',
                        'reason': f'High inventory ({product.inventory} units)',
                        'current_price': product.current_price,
                        'recommended_price': round(new_price, 2),
                        'expected_impact': f'-{recommended_decrease*100:.1f}% price decrease to move inventory',
                        'priority': 'low'
                    })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting recommendations for product {product.id}: {str(e)}")
            return [] 