from flask import Blueprint, request, jsonify
from app import db
from models.product import Product
from models.sales import Sales
import json

bp = Blueprint('products', __name__, url_prefix='/api/products')

@bp.route('', methods=['GET'])
def get_products():
    """Get all products with optional filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')
        search = request.args.get('search')
        
        query = Product.query
        
        if category:
            query = query.filter(Product.category == category)
        
        if search:
            query = query.filter(Product.name.contains(search))
        
        products = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'products': [product.to_dict() for product in products.items],
            'total': products.total,
            'pages': products.pages,
            'current_page': page,
            'per_page': per_page
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID"""
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_dict())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('', methods=['POST'])
def create_product():
    """Create a new product"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['id', 'name', 'base_price', 'cost_price', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if product ID already exists
        if Product.query.get(data['id']):
            return jsonify({'error': 'Product ID already exists'}), 400
        
        product = Product(
            id=data['id'],
            name=data['name'],
            base_price=data['base_price'],
            cost_price=data['cost_price'],
            inventory=data.get('inventory', 0),
            sales_last_30_days=data.get('sales_last_30_days', 0),
            average_rating=data.get('average_rating', 0.0),
            category=data['category'],
            description=data.get('description', '')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify(product.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<product_id>', methods=['PUT'])
def update_product(product_id):
    """Update an existing product"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            product.name = data['name']
        if 'base_price' in data:
            product.base_price = data['base_price']
        if 'cost_price' in data:
            product.cost_price = data['cost_price']
        if 'inventory' in data:
            product.inventory = data['inventory']
        if 'sales_last_30_days' in data:
            product.sales_last_30_days = data['sales_last_30_days']
        if 'average_rating' in data:
            product.average_rating = data['average_rating']
        if 'category' in data:
            product.category = data['category']
        if 'description' in data:
            product.description = data['description']
        
        db.session.commit()
        
        return jsonify(product.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({'message': 'Product deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<product_id>/sales', methods=['GET'])
def get_product_sales(product_id):
    """Get sales history for a specific product"""
    try:
        Product.query.get_or_404(product_id)  # Ensure product exists
        
        sales = Sales.query.filter_by(product_id=product_id).order_by(Sales.date.desc()).all()
        
        return jsonify([sale.to_dict() for sale in sales])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all product categories"""
    try:
        categories = db.session.query(Product.category).distinct().all()
        return jsonify([category[0] for category in categories])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500 