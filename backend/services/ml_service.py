import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
import logging
from datetime import datetime, timedelta
import json

class MLService:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        self.model_path = 'models/pricing_model.pkl'
        self.scaler_path = 'models/scaler.pkl'
        self.encoders_path = 'models/encoders.pkl'
        self.logger = logging.getLogger(__name__)
        
        # Ensure models directory exists
        os.makedirs('models', exist_ok=True)
        
        # Load existing model if available
        self.load_model()
    
    def prepare_features(self, product, sales_data=None):
        """
        Prepare features for ML model prediction
        """
        try:
            features = {
                'base_price': product.base_price,
                'cost_price': product.cost_price,
                'inventory': product.inventory,
                'sales_last_30_days': product.sales_last_30_days,
                'average_rating': product.average_rating,
                'category': product.category,
                'current_price': product.current_price,
                'inventory_ratio': product.inventory / max(product.sales_last_30_days, 1),
                'price_to_cost_ratio': product.current_price / product.cost_price,
                'profit_margin': ((product.current_price - product.cost_price) / product.cost_price) * 100,
                'demand_indicator': product.sales_last_30_days / max(product.inventory, 1),
                'rating_impact': (product.average_rating - 3.0) * 10,  # Normalize rating impact
            }
            
            # Add seasonal features (simplified)
            current_month = datetime.now().month
            features['month'] = current_month
            features['is_holiday_season'] = 1 if current_month in [11, 12] else 0
            features['is_summer'] = 1 if current_month in [6, 7, 8] else 0
            
            # Add category-specific features
            category_avg_price = self._get_category_average_price(product.category)
            features['category_price_position'] = product.current_price / max(category_avg_price, 1)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error preparing features: {str(e)}")
            return None
    
    def train_model(self, products, sales_data=None):
        """
        Train the ML model for price prediction
        """
        try:
            if len(products) < 10:
                self.logger.warning("Insufficient data for training. Need at least 10 products.")
                return False
            
            # Prepare training data
            training_data = []
            targets = []
            
            for product in products:
                features = self.prepare_features(product, sales_data)
                if features:
                    training_data.append(features)
                    # Target: optimal price based on current performance
                    # This is simplified - in real scenario, you'd use historical performance data
                    target_price = self._calculate_target_price(product)
                    targets.append(target_price)
            
            if len(training_data) == 0:
                self.logger.error("No valid training data prepared")
                return False
            
            # Convert to DataFrame
            df = pd.DataFrame(training_data)
            self.feature_columns = df.columns.tolist()
            
            # Encode categorical variables
            categorical_columns = ['category']
            for col in categorical_columns:
                if col in df.columns:
                    if col not in self.label_encoders:
                        self.label_encoders[col] = LabelEncoder()
                    df[col] = self.label_encoders[col].fit_transform(df[col].astype(str))
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                df.values, targets, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train ensemble model
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            
            rf_model.fit(X_train_scaled, y_train)
            gb_model.fit(X_train_scaled, y_train)
            
            # Create ensemble predictions
            rf_pred = rf_model.predict(X_test_scaled)
            gb_pred = gb_model.predict(X_test_scaled)
            
            # Simple ensemble: average of both models
            ensemble_pred = (rf_pred + gb_pred) / 2
            
            # Evaluate model
            mse = mean_squared_error(y_test, ensemble_pred)
            r2 = r2_score(y_test, ensemble_pred)
            
            self.logger.info(f"Model training completed. MSE: {mse:.2f}, R2: {r2:.3f}")
            
            # Store models
            self.model = {
                'rf': rf_model,
                'gb': gb_model,
                'ensemble_weights': [0.5, 0.5]  # Equal weights for now
            }
            
            # Save model and preprocessors
            self.save_model()
            
            # Calculate feature importance
            feature_importance = self._calculate_feature_importance()
            
            # Save model info
            self._save_model_info({
                'success': True,
                'mse': mse,
                'r2_score': r2,
                'training_samples': len(training_data),
                'feature_importance': feature_importance
            })
            
            return {
                'success': True,
                'mse': mse,
                'r2_score': r2,
                'feature_importance': feature_importance,
                'training_samples': len(training_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error training model: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def predict_optimal_price(self, product):
        """
        Predict optimal price for a product
        """
        try:
            if not self.model:
                # If no trained model, use simple heuristic
                return self._heuristic_pricing(product)
            
            features = self.prepare_features(product)
            if not features:
                return self._heuristic_pricing(product)
            
            # Convert features to DataFrame with correct column order
            feature_df = pd.DataFrame([features])[self.feature_columns]
            
            # Encode categorical variables
            for col in ['category']:
                if col in feature_df.columns and col in self.label_encoders:
                    try:
                        feature_df[col] = self.label_encoders[col].transform(feature_df[col].astype(str))
                    except ValueError:
                        # Handle unseen categories
                        feature_df[col] = 0
            
            # Scale features
            features_scaled = self.scaler.transform(feature_df.values)
            
            # Make predictions with ensemble
            rf_pred = self.model['rf'].predict(features_scaled)[0]
            gb_pred = self.model['gb'].predict(features_scaled)[0]
            
            weights = self.model['ensemble_weights']
            ensemble_pred = rf_pred * weights[0] + gb_pred * weights[1]
            
            # Apply business logic constraints
            min_price = product.get_min_price()
            max_price = product.get_max_price()
            
            predicted_price = max(min_price, min(max_price, ensemble_pred))
            
            return predicted_price
            
        except Exception as e:
            self.logger.error(f"Error predicting price for product {product.id}: {str(e)}")
            return self._heuristic_pricing(product)
    
    def _heuristic_pricing(self, product):
        """
        Simple heuristic pricing when ML model is not available
        """
        base_price = product.current_price
        
        # Inventory-based adjustment
        if product.inventory < 5:
            base_price *= 1.2  # Increase by 20% for very low inventory
        elif product.inventory < 10:
            base_price *= 1.1  # Increase by 10% for low inventory
        elif product.inventory > 50:
            base_price *= 0.95  # Decrease by 5% for high inventory
        
        # Rating-based adjustment
        if product.average_rating > 4.5:
            base_price *= 1.05  # Premium for high-rated products
        elif product.average_rating < 3.0:
            base_price *= 0.95  # Discount for low-rated products
        
        # Sales performance adjustment
        expected_sales = product.inventory * 0.3  # 30% turnover expectation
        if product.sales_last_30_days > expected_sales * 1.5:
            base_price *= 1.05  # High demand, increase price
        elif product.sales_last_30_days < expected_sales * 0.5:
            base_price *= 0.95  # Low demand, decrease price
        
        # Ensure constraints
        min_price = product.get_min_price()
        max_price = product.get_max_price()
        
        return max(min_price, min(max_price, base_price))
    
    def _calculate_target_price(self, product):
        """
        Calculate target price for training (simplified approach)
        """
        # This is a simplified target calculation
        # In real scenario, you'd use historical data to determine optimal prices
        
        base_target = product.current_price
        
        # Adjust based on performance indicators
        performance_score = 0
        
        # Inventory efficiency
        if product.inventory > 0:
            turnover_rate = product.sales_last_30_days / product.inventory
            if turnover_rate > 1.0:  # Fast moving
                performance_score += 0.1
            elif turnover_rate < 0.3:  # Slow moving
                performance_score -= 0.1
        
        # Rating impact
        if product.average_rating > 4.0:
            performance_score += 0.05
        elif product.average_rating < 3.5:
            performance_score -= 0.05
        
        # Profit margin consideration
        current_margin = product.get_profit_margin()
        if current_margin < 15:  # Low margin
            performance_score += 0.1  # Target higher price
        elif current_margin > 40:  # High margin
            performance_score -= 0.05  # Could afford lower price
        
        target_price = base_target * (1 + performance_score)
        
        # Ensure constraints
        min_price = product.get_min_price()
        max_price = product.get_max_price()
        
        return max(min_price, min(max_price, target_price))
    
    def _calculate_feature_importance(self):
        """
        Calculate and return feature importance
        """
        if not self.model or not self.feature_columns:
            return {}
        
        try:
            # Get feature importance from Random Forest
            rf_importance = self.model['rf'].feature_importances_
            
            importance_dict = {}
            for i, feature in enumerate(self.feature_columns):
                importance_dict[feature] = float(rf_importance[i])
            
            # Sort by importance
            sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
            
            return dict(sorted_importance)
            
        except Exception as e:
            self.logger.error(f"Error calculating feature importance: {str(e)}")
            return {}
    
    def _get_category_average_price(self, category):
        """
        Get average price for a category (simplified implementation)
        """
        # This would typically query the database
        # For now, return category-based estimates
        category_prices = {
            'Electronics': 150,
            'Apparel': 80,
            'Home': 60,
            'Books': 25,
            'Luxury': 300
        }
        return category_prices.get(category, 100)
    
    def save_model(self):
        """
        Save trained model and preprocessors
        """
        try:
            if self.model:
                joblib.dump(self.model, self.model_path)
                joblib.dump(self.scaler, self.scaler_path)
                joblib.dump({
                    'label_encoders': self.label_encoders,
                    'feature_columns': self.feature_columns
                }, self.encoders_path)
                self.logger.info("Model saved successfully")
                return True
        except Exception as e:
            self.logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self):
        """
        Load trained model and preprocessors
        """
        try:
            if (os.path.exists(self.model_path) and 
                os.path.exists(self.scaler_path) and 
                os.path.exists(self.encoders_path)):
                
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                
                encoder_data = joblib.load(self.encoders_path)
                self.label_encoders = encoder_data['label_encoders']
                self.feature_columns = encoder_data['feature_columns']
                
                self.logger.info("Model loaded successfully")
                return True
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            
        return False
    
    def get_model_info(self):
        """Get information about the current model state"""
        try:
            model_info = {
                'last_training': None,
                'training_samples': 0,
                'mse': None,
                'r2_score': None,
                'feature_importance': [],
                'training_history': []
            }
            
            # Load model info from file if exists
            info_path = os.path.join('models', 'model_info.json')
            if os.path.exists(info_path):
                with open(info_path, 'r') as f:
                    model_info = json.load(f)
            
            # Add current model metrics if model is loaded
            if self.model is not None:
                model_info['feature_importance'] = self._calculate_feature_importance()
            
            return model_info
            
        except Exception as e:
            self.logger.error(f"Error getting model info: {str(e)}")
            return None

    def _save_model_info(self, training_metrics):
        """Save model information and training metrics"""
        try:
            info_path = os.path.join('models', 'model_info.json')
            
            # Load existing info if available
            model_info = {
                'last_training': datetime.now().isoformat(),
                'training_samples': training_metrics.get('training_samples', 0),
                'mse': training_metrics.get('mse'),
                'r2_score': training_metrics.get('r2_score'),
                'feature_importance': training_metrics.get('feature_importance', []),
                'training_history': []
            }
            
            if os.path.exists(info_path):
                with open(info_path, 'r') as f:
                    existing_info = json.load(f)
                    model_info['training_history'] = existing_info.get('training_history', [])
            
            # Add current training metrics to history
            model_info['training_history'].append({
                'date': model_info['last_training'],
                'mse': model_info['mse'],
                'r2_score': model_info['r2_score'],
                'training_samples': model_info['training_samples']
            })
            
            # Keep only last 10 training records
            model_info['training_history'] = model_info['training_history'][-10:]
            
            # Save updated info
            with open(info_path, 'w') as f:
                json.dump(model_info, f, indent=2)
            
            return model_info
            
        except Exception as e:
            self.logger.error(f"Error saving model info: {str(e)}")
            return None 