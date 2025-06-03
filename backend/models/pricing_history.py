from datetime import datetime
from app import db

class PricingHistory(db.Model):
    __tablename__ = 'pricing_history'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(10), db.ForeignKey('products.id'), nullable=False)
    old_price = db.Column(db.Float, nullable=False)
    new_price = db.Column(db.Float, nullable=False)
    adjustment_reason = db.Column(db.String(200), nullable=False)
    adjustment_type = db.Column(db.String(50), nullable=False)  # AI_PREDICTION, INVENTORY_LOW, COMPETITOR_PRICE, etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, product_id, old_price, new_price, adjustment_reason, adjustment_type):
        self.product_id = product_id
        self.old_price = old_price
        self.new_price = new_price
        self.adjustment_reason = adjustment_reason
        self.adjustment_type = adjustment_type
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'old_price': self.old_price,
            'new_price': self.new_price,
            'adjustment_reason': self.adjustment_reason,
            'adjustment_type': self.adjustment_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'price_change_percent': round(((self.new_price - self.old_price) / self.old_price) * 100, 2)
        } 