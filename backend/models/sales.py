from datetime import datetime
from app import db

class Sales(db.Model):
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(10), db.ForeignKey('products.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    units_sold = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    revenue = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, product_id, date, units_sold, price):
        self.product_id = product_id
        self.date = date
        self.units_sold = units_sold
        self.price = price
        self.revenue = units_sold * price
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'date': self.date.isoformat() if self.date else None,
            'units_sold': self.units_sold,
            'price': self.price,
            'revenue': self.revenue,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 