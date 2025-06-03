from datetime import datetime
from app import db

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    inventory = db.Column(db.Integer, nullable=False, default=0)
    sales_last_30_days = db.Column(db.Integer, nullable=False, default=0)
    average_rating = db.Column(db.Float, nullable=False, default=0.0)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sales = db.relationship('Sales', backref='product', lazy=True, cascade='all, delete-orphan')
    pricing_history = db.relationship('PricingHistory', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, id, name, base_price, cost_price, inventory=0, sales_last_30_days=0, 
                 average_rating=0.0, category='', description=''):
        self.id = id
        self.name = name
        self.base_price = base_price
        self.current_price = base_price
        self.cost_price = cost_price
        self.inventory = inventory
        self.sales_last_30_days = sales_last_30_days
        self.average_rating = average_rating
        self.category = category
        self.description = description
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'base_price': self.base_price,
            'current_price': self.current_price,
            'cost_price': self.cost_price,
            'inventory': self.inventory,
            'sales_last_30_days': self.sales_last_30_days,
            'average_rating': self.average_rating,
            'category': self.category,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_profit_margin(self):
        """Calculate current profit margin percentage"""
        return ((self.current_price - self.cost_price) / self.cost_price) * 100
    
    def get_min_price(self):
        """Get minimum allowable price (cost + 10%)"""
        return self.cost_price * 1.10
    
    def get_max_price(self):
        """Get maximum allowable price (base price + 50%)"""
        return self.base_price * 1.50
    
    def is_low_inventory(self, threshold=10):
        """Check if inventory is below threshold"""
        return self.inventory <= threshold
    
    def update_price(self, new_price):
        """Update product price with validation"""
        min_price = self.get_min_price()
        max_price = self.get_max_price()
        
        if new_price < min_price:
            new_price = min_price
        elif new_price > max_price:
            new_price = max_price
            
        self.current_price = round(new_price, 2)
        self.updated_at = datetime.utcnow()
        
        return self.current_price 