from flask import Blueprint, request, jsonify
from app import db
from models.product import Product
from models.pricing_history import PricingHistory
from services.pricing_service import PricingService
from services.competitor_service import CompetitorService
from services.ml_service import MLService
import requests

bp = Blueprint('pricing', __name__, url_prefix='/api/pricing')

@bp.route('/optimize', methods=['POST'])
def optimize_pricing():
    """Run dynamic pricing optimization for all products or specific products"""
    try:
        data = request.get_json() or {}
        product_ids = data.get('product_ids', [])
        
        if product_ids:
            products = Product.query.filter(Product.id.in_(product_ids)).all()
        else:
            products = Product.query.all()
        
        if not products:
            return jsonify({'error': 'No products found'}), 404
        
        pricing_service = PricingService()
        ml_service = MLService()
        competitor_service = CompetitorService()
        
        results = []
        
        for product in products:
            try:
                # Get ML prediction
                ml_prediction = ml_service.predict_optimal_price(product)
                
                # Get competitor pricing
                competitor_price = competitor_service.get_competitor_price(product.id)
                
                # Apply dynamic pricing logic
                optimization_result = pricing_service.optimize_price(
                    product, ml_prediction, competitor_price
                )
                
                results.append(optimization_result)
                
            except Exception as e:
                results.append({
                    'product_id': product.id,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'message': 'Pricing optimization completed',
            'results': results,
            'total_processed': len(results),
            'successful': len([r for r in results if r.get('success', False)])
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/product/<product_id>/optimize', methods=['POST'])
def optimize_single_product_pricing(product_id):
    """Optimize pricing for a single product"""
    try:
        product = Product.query.get_or_404(product_id)
        
        pricing_service = PricingService()
        ml_service = MLService()
        competitor_service = CompetitorService()
        
        # Get ML prediction
        ml_prediction = ml_service.predict_optimal_price(product)
        
        # Get competitor pricing
        competitor_price = competitor_service.get_competitor_price(product.id)
        
        # Apply dynamic pricing logic
        result = pricing_service.optimize_price(product, ml_prediction, competitor_price)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/product/<product_id>/price', methods=['PUT'])
def update_product_price(product_id):
    """Manually update product price"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        if 'price' not in data:
            return jsonify({'error': 'Price is required'}), 400
        
        new_price = float(data['price'])
        reason = data.get('reason', 'Manual price adjustment')
        
        old_price = product.current_price
        
        # Validate price bounds
        min_price = product.get_min_price()
        max_price = product.get_max_price()
        
        if new_price < min_price:
            return jsonify({
                'error': f'Price cannot be below minimum price of ${min_price:.2f}'
            }), 400
        
        if new_price > max_price:
            return jsonify({
                'error': f'Price cannot be above maximum price of ${max_price:.2f}'
            }), 400
        
        # Update price
        product.update_price(new_price)
        
        # Record pricing history
        pricing_history = PricingHistory(
            product_id=product.id,
            old_price=old_price,
            new_price=new_price,
            adjustment_reason=reason,
            adjustment_type='MANUAL_ADJUSTMENT'
        )
        
        db.session.add(pricing_history)
        db.session.commit()
        
        return jsonify({
            'message': 'Price updated successfully',
            'product': product.to_dict(),
            'pricing_history': pricing_history.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/product/<product_id>/history', methods=['GET'])
def get_pricing_history(product_id):
    """Get pricing history for a product"""
    try:
        Product.query.get_or_404(product_id)  # Ensure product exists
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        history = PricingHistory.query.filter_by(product_id=product_id)\
            .order_by(PricingHistory.timestamp.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'history': [record.to_dict() for record in history.items],
            'total': history.total,
            'pages': history.pages,
            'current_page': page,
            'per_page': per_page
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/competitor-prices', methods=['GET'])
def get_competitor_prices():
    """Get competitor prices for all products"""
    try:
        competitor_service = CompetitorService()
        products = Product.query.all()
        competitor_prices = {item['product_id']: item['competitor_price'] for item in competitor_service.fetch_competitor_prices()}

        competitor_data = []
        for product in products:
            competitor_price = competitor_prices.get(product.id)
            price_difference = product.current_price - competitor_price if competitor_price is not None else None
            if competitor_price is not None:
                if product.current_price > competitor_price:
                    position = 'higher'
                elif product.current_price < competitor_price:
                    position = 'lower'
                else:
                    position = 'equal'
            else:
                position = 'unknown'
            competitor_data.append({
                'product_id': product.id,
                'our_price': product.current_price,
                'competitor_price': competitor_price,
                'price_difference': price_difference,
                'competitive_position': position
            })

        return jsonify(competitor_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/analytics', methods=['GET'])
def get_pricing_analytics():
    """Get pricing analytics and insights"""
    try:
        # Get all products
        products = Product.query.all()
        
        total_products = len(products)
        low_inventory_products = len([p for p in products if p.is_low_inventory()])
        
        # Calculate average metrics
        avg_profit_margin = sum([p.get_profit_margin() for p in products]) / total_products if total_products > 0 else 0
        
        # Get recent pricing adjustments
        recent_adjustments = PricingHistory.query.order_by(PricingHistory.timestamp.desc()).limit(10).all()
        
        # Category analysis
        category_stats = {}
        for product in products:
            category = product.category
            if category not in category_stats:
                category_stats[category] = {
                    'count': 0,
                    'avg_price': 0,
                    'avg_margin': 0,
                    'total_sales': 0
                }
            
            category_stats[category]['count'] += 1
            category_stats[category]['total_sales'] += product.sales_last_30_days
        
        # Calculate averages for categories
        for category, stats in category_stats.items():
            category_products = [p for p in products if p.category == category]
            stats['avg_price'] = sum([p.current_price for p in category_products]) / len(category_products)
            stats['avg_margin'] = sum([p.get_profit_margin() for p in category_products]) / len(category_products)
        
        return jsonify({
            'summary': {
                'total_products': total_products,
                'low_inventory_products': low_inventory_products,
                'average_profit_margin': round(avg_profit_margin, 2)
            },
            'recent_adjustments': [adj.to_dict() for adj in recent_adjustments],
            'category_stats': category_stats
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/model/train', methods=['POST'])
def train_model():
    """Train or retrain the ML model"""
    try:
        from services.ml_service import MLService
        from models.product import Product
        
        # Get all products for training
        products = Product.query.all()
        
        if len(products) < 10:
            return jsonify({
                'success': False,
                'error': 'Insufficient data for training. Need at least 10 products.'
            }), 400
        
        # Initialize and train model
        ml_service = MLService()
        training_result = ml_service.train_model(products)
        
        if not training_result.get('success'):
            return jsonify({
                'success': False,
                'error': training_result.get('error', 'Training failed')
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Model trained successfully',
            'training_metrics': {
                'mse': training_result.get('mse'),
                'r2_score': training_result.get('r2_score'),
                'training_samples': training_result.get('training_samples'),
                'feature_importance': training_result.get('feature_importance')
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/model/info', methods=['GET'])
def get_model_info():
    """Get information about the current ML model"""
    try:
        from services.ml_service import MLService
        
        ml_service = MLService()
        model_info = ml_service.get_model_info()
        
        return jsonify({
            'success': True,
            'model_info': model_info
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500 