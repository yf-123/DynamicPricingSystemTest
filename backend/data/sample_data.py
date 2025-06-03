import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from models.product import Product
from models.sales import Sales
from datetime import datetime, timedelta
import random

app = create_app()

def create_sample_products():
    """Create sample products"""
    products_data = [
        {
            'id': 'P001',
            'name': 'Wireless Bluetooth Headphones',
            'base_price': 100.0,
            'cost_price': 60.0,
            'inventory': 15,
            'sales_last_30_days': 120,
            'average_rating': 4.5,
            'category': 'Electronics',
            'description': 'Premium wireless headphones with noise cancellation'
        },
        {
            'id': 'P002',
            'name': 'Designer Cotton T-Shirt',
            'base_price': 200.0,
            'cost_price': 80.0,
            'inventory': 50,
            'sales_last_30_days': 40,
            'average_rating': 4.0,
            'category': 'Apparel',
            'description': 'Comfortable premium cotton t-shirt'
        },
        {
            'id': 'P003',
            'name': 'Smart Home Security Camera',
            'base_price': 50.0,
            'cost_price': 25.0,
            'inventory': 5,
            'sales_last_30_days': 10,
            'average_rating': 3.8,
            'category': 'Home',
            'description': 'WiFi-enabled security camera with mobile app'
        },
        {
            'id': 'P004',
            'name': 'Gaming Mechanical Keyboard',
            'base_price': 150.0,
            'cost_price': 90.0,
            'inventory': 25,
            'sales_last_30_days': 75,
            'average_rating': 4.7,
            'category': 'Electronics',
            'description': 'RGB backlit mechanical keyboard for gaming'
        },
        {
            'id': 'P005',
            'name': 'Premium Leather Jacket',
            'base_price': 300.0,
            'cost_price': 150.0,
            'inventory': 8,
            'sales_last_30_days': 15,
            'average_rating': 4.3,
            'category': 'Apparel',
            'description': 'Genuine leather jacket with modern fit'
        },
        {
            'id': 'P006',
            'name': 'Smart WiFi Thermostat',
            'base_price': 120.0,
            'cost_price': 70.0,
            'inventory': 30,
            'sales_last_30_days': 45,
            'average_rating': 4.1,
            'category': 'Home',
            'description': 'Energy-efficient smart thermostat with app control'
        },
        {
            'id': 'P007',
            'name': 'Portable Power Bank',
            'base_price': 45.0,
            'cost_price': 20.0,
            'inventory': 100,
            'sales_last_30_days': 200,
            'average_rating': 4.0,
            'category': 'Electronics',
            'description': '20000mAh portable charger with fast charging'
        },
        {
            'id': 'P008',
            'name': 'Yoga Mat Premium',
            'base_price': 80.0,
            'cost_price': 35.0,
            'inventory': 40,
            'sales_last_30_days': 60,
            'average_rating': 4.4,
            'category': 'Home',
            'description': 'Non-slip premium yoga mat with carrying strap'
        },
        {
            'id': 'P009',
            'name': 'Running Sneakers',
            'base_price': 180.0,
            'cost_price': 90.0,
            'inventory': 35,
            'sales_last_30_days': 85,
            'average_rating': 4.2,
            'category': 'Apparel',
            'description': 'Lightweight running shoes with cushioned sole'
        },
        {
            'id': 'P010',
            'name': 'Coffee Maker Deluxe',
            'base_price': 220.0,
            'cost_price': 120.0,
            'inventory': 12,
            'sales_last_30_days': 25,
            'average_rating': 4.6,
            'category': 'Home',
            'description': 'Programmable coffee maker with thermal carafe'
        }
    ]
    
    for product_data in products_data:
        # Check if product already exists
        existing_product = Product.query.get(product_data['id'])
        if not existing_product:
            product = Product(**product_data)
            db.session.add(product)
    
    db.session.commit()
    print(f"Created {len(products_data)} sample products")

def create_sample_sales():
    """Create sample sales data"""
    products = Product.query.all()
    
    if not products:
        print("No products found. Create products first.")
        return
    
    # Generate sales data for the last 60 days
    start_date = datetime.now().date() - timedelta(days=60)
    
    sales_data = []
    for product in products:
        # Generate realistic sales pattern
        base_daily_sales = product.sales_last_30_days // 30
        
        for day in range(60):
            current_date = start_date + timedelta(days=day)
            
            # Add some randomness to daily sales
            daily_sales = max(0, int(base_daily_sales + random.randint(-2, 3)))
            
            # Weekend boost for some categories
            if current_date.weekday() >= 5:  # Weekend
                if product.category in ['Electronics', 'Home']:
                    daily_sales = int(daily_sales * 1.3)
            
            # Holiday season boost (November-December)
            if current_date.month in [11, 12]:
                daily_sales = int(daily_sales * 1.5)
            
            if daily_sales > 0:
                # Price might vary slightly over time
                price_variation = random.uniform(-0.05, 0.05)  # ±5%
                sale_price = product.current_price * (1 + price_variation)
                
                sales_data.append({
                    'product_id': product.id,
                    'date': current_date,
                    'units_sold': daily_sales,
                    'price': round(sale_price, 2)
                })
    
    # Create sales records
    for sale_data in sales_data:
        sale = Sales(**sale_data)
        db.session.add(sale)
    
    db.session.commit()
    print(f"Created {len(sales_data)} sample sales records")

def initialize_sample_data():
    """Initialize all sample data"""
    with app.app_context():
        db.create_all()
        create_sample_products()
        create_sample_sales()
        print("Sample data initialization completed!")

if __name__ == '__main__':
    initialize_sample_data() 