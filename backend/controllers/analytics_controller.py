from flask import Blueprint, request, jsonify
from app import db
from models.product import Product
from models.sales import Sales
from models.pricing_history import PricingHistory
from sqlalchemy import func
from datetime import datetime, timedelta
import json

bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get comprehensive dashboard analytics"""
    try:
        # Basic metrics
        total_products = Product.query.count()
        total_sales = db.session.query(func.sum(Sales.units_sold)).scalar() or 0
        total_revenue = db.session.query(func.sum(Sales.revenue)).scalar() or 0
        
        # Low inventory count
        low_inventory_count = Product.query.filter(Product.inventory <= 10).count()
        
        # Recent sales (last 7 days)
        week_ago = datetime.utcnow().date() - timedelta(days=7)
        recent_sales = db.session.query(func.sum(Sales.units_sold))\
            .filter(Sales.date >= week_ago).scalar() or 0
        
        # Category performance
        category_performance = db.session.query(
            Product.category,
            func.count(Product.id).label('product_count'),
            func.avg(Product.current_price).label('avg_price'),
            func.sum(Product.sales_last_30_days).label('total_sales')
        ).group_by(Product.category).all()
        
        # Top performing products
        top_products = Product.query.order_by(Product.sales_last_30_days.desc()).limit(10).all()
        
        # Recent pricing changes
        recent_pricing_changes = PricingHistory.query\
            .order_by(PricingHistory.timestamp.desc()).limit(10).all()
        
        return jsonify({
            'summary': {
                'total_products': total_products,
                'total_sales': int(total_sales),
                'total_revenue': round(float(total_revenue), 2),
                'low_inventory_count': low_inventory_count,
                'recent_sales_7_days': int(recent_sales)
            },
            'category_performance': [
                {
                    'category': row.category,
                    'product_count': row.product_count,
                    'avg_price': round(float(row.avg_price), 2),
                    'total_sales': int(row.total_sales or 0)
                }
                for row in category_performance
            ],
            'top_products': [product.to_dict() for product in top_products],
            'recent_pricing_changes': [change.to_dict() for change in recent_pricing_changes]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/sales-trends', methods=['GET'])
def get_sales_trends():
    """Get sales trends over time"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow().date() - timedelta(days=days)
        
        # Daily sales data
        daily_sales = db.session.query(
            Sales.date,
            func.sum(Sales.units_sold).label('units_sold'),
            func.sum(Sales.revenue).label('revenue')
        ).filter(Sales.date >= start_date)\
         .group_by(Sales.date)\
         .order_by(Sales.date).all()
        
        # Category trends
        category_trends = db.session.query(
            Product.category,
            Sales.date,
            func.sum(Sales.units_sold).label('units_sold'),
            func.sum(Sales.revenue).label('revenue')
        ).join(Product)\
         .filter(Sales.date >= start_date)\
         .group_by(Product.category, Sales.date)\
         .order_by(Sales.date).all()
        
        # Format daily sales data
        daily_data = [
            {
                'date': row.date.isoformat(),
                'units_sold': int(row.units_sold),
                'revenue': round(float(row.revenue), 2)
            }
            for row in daily_sales
        ]
        
        # Format category trends
        category_data = {}
        for row in category_trends:
            if row.category not in category_data:
                category_data[row.category] = []
            
            category_data[row.category].append({
                'date': row.date.isoformat(),
                'units_sold': int(row.units_sold),
                'revenue': round(float(row.revenue), 2)
            })
        
        return jsonify({
            'daily_sales': daily_data,
            'category_trends': category_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/inventory-analysis', methods=['GET'])
def get_inventory_analysis():
    """Get inventory analysis and alerts"""
    try:
        # Products by inventory status
        critical_inventory = Product.query.filter(Product.inventory <= 5).all()
        low_inventory = Product.query.filter(Product.inventory.between(6, 20)).all()
        normal_inventory = Product.query.filter(Product.inventory > 20).all()
        
        # Inventory turnover analysis
        high_turnover = Product.query.filter(
            Product.sales_last_30_days > Product.inventory * 0.5
        ).all()
        
        slow_moving = Product.query.filter(
            Product.sales_last_30_days < Product.inventory * 0.1
        ).all()
        
        # Category inventory distribution
        category_inventory = db.session.query(
            Product.category,
            func.sum(Product.inventory).label('total_inventory'),
            func.avg(Product.inventory).label('avg_inventory'),
            func.count(Product.id).label('product_count')
        ).group_by(Product.category).all()
        
        return jsonify({
            'inventory_status': {
                'critical': [product.to_dict() for product in critical_inventory],
                'low': [product.to_dict() for product in low_inventory],
                'normal_count': len(normal_inventory)
            },
            'turnover_analysis': {
                'high_turnover': [product.to_dict() for product in high_turnover],
                'slow_moving': [product.to_dict() for product in slow_moving]
            },
            'category_inventory': [
                {
                    'category': row.category,
                    'total_inventory': int(row.total_inventory),
                    'avg_inventory': round(float(row.avg_inventory), 2),
                    'product_count': row.product_count
                }
                for row in category_inventory
            ]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/pricing-impact', methods=['GET'])
def get_pricing_impact():
    """Analyze the impact of pricing changes"""
    try:
        # Get products with recent price changes
        recent_changes = db.session.query(PricingHistory)\
            .filter(PricingHistory.timestamp >= datetime.utcnow() - timedelta(days=30))\
            .all()
        
        impact_analysis = []
        
        for change in recent_changes:
            product = Product.query.get(change.product_id)
            if not product:
                continue
            
            # Calculate sales before and after price change
            change_date = change.timestamp.date()
            before_date = change_date - timedelta(days=7)
            after_date = change_date + timedelta(days=7)
            
            sales_before = db.session.query(func.sum(Sales.units_sold))\
                .filter(Sales.product_id == product.id)\
                .filter(Sales.date.between(before_date, change_date))\
                .scalar() or 0
            
            sales_after = db.session.query(func.sum(Sales.units_sold))\
                .filter(Sales.product_id == product.id)\
                .filter(Sales.date.between(change_date, after_date))\
                .scalar() or 0
            
            impact_analysis.append({
                'product_id': product.id,
                'product_name': product.name,
                'price_change': change.to_dict(),
                'sales_before': int(sales_before),
                'sales_after': int(sales_after),
                'sales_impact': int(sales_after - sales_before),
                'sales_impact_percent': round(
                    ((sales_after - sales_before) / sales_before * 100) if sales_before > 0 else 0, 2
                )
            })
        
        # Price elasticity analysis
        elasticity_data = []
        for product in Product.query.limit(20).all():  # Limit for performance
            price_changes = PricingHistory.query.filter_by(product_id=product.id)\
                .order_by(PricingHistory.timestamp.desc()).limit(5).all()
            
            if len(price_changes) >= 2:
                # Calculate simple elasticity between first and last price change
                first_change = price_changes[-1]
                last_change = price_changes[0]
                
                price_change_percent = ((last_change.new_price - first_change.old_price) / first_change.old_price) * 100
                
                # Get sales data for periods
                sales_period1 = db.session.query(func.sum(Sales.units_sold))\
                    .filter(Sales.product_id == product.id)\
                    .filter(Sales.date <= first_change.timestamp.date())\
                    .scalar() or 1
                
                sales_period2 = db.session.query(func.sum(Sales.units_sold))\
                    .filter(Sales.product_id == product.id)\
                    .filter(Sales.date >= last_change.timestamp.date())\
                    .scalar() or 1
                
                sales_change_percent = ((sales_period2 - sales_period1) / sales_period1) * 100
                
                elasticity = sales_change_percent / price_change_percent if price_change_percent != 0 else 0
                
                elasticity_data.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'price_elasticity': round(elasticity, 3),
                    'interpretation': 'elastic' if abs(elasticity) > 1 else 'inelastic'
                })
        
        return jsonify({
            'pricing_impact': impact_analysis,
            'price_elasticity': elasticity_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reports/monthly', methods=['GET'])
def generate_monthly_report():
    """Generate monthly performance report"""
    try:
        # Get date range
        year = request.args.get('year', datetime.utcnow().year, type=int)
        month = request.args.get('month', datetime.utcnow().month, type=int)
        
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month + 1, 1).date()
        
        # Sales summary
        monthly_sales = db.session.query(
            func.sum(Sales.units_sold).label('total_units'),
            func.sum(Sales.revenue).label('total_revenue'),
            func.count(Sales.id).label('total_transactions')
        ).filter(Sales.date.between(start_date, end_date)).first()
        
        # Top products
        top_products = db.session.query(
            Product.id,
            Product.name,
            func.sum(Sales.units_sold).label('units_sold'),
            func.sum(Sales.revenue).label('revenue')
        ).join(Sales)\
         .filter(Sales.date.between(start_date, end_date))\
         .group_by(Product.id, Product.name)\
         .order_by(func.sum(Sales.revenue).desc())\
         .limit(10).all()
        
        # Category performance
        category_performance = db.session.query(
            Product.category,
            func.sum(Sales.units_sold).label('units_sold'),
            func.sum(Sales.revenue).label('revenue')
        ).join(Sales)\
         .filter(Sales.date.between(start_date, end_date))\
         .group_by(Product.category).all()
        
        # Pricing adjustments
        pricing_adjustments = PricingHistory.query\
            .filter(PricingHistory.timestamp.between(start_date, end_date))\
            .count()
        
        return jsonify({
            'report_period': {
                'year': year,
                'month': month,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'sales_summary': {
                'total_units': int(monthly_sales.total_units or 0),
                'total_revenue': round(float(monthly_sales.total_revenue or 0), 2),
                'total_transactions': monthly_sales.total_transactions or 0
            },
            'top_products': [
                {
                    'product_id': row.id,
                    'product_name': row.name,
                    'units_sold': int(row.units_sold),
                    'revenue': round(float(row.revenue), 2)
                }
                for row in top_products
            ],
            'category_performance': [
                {
                    'category': row.category,
                    'units_sold': int(row.units_sold),
                    'revenue': round(float(row.revenue), 2)
                }
                for row in category_performance
            ],
            'pricing_adjustments_count': pricing_adjustments
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500 