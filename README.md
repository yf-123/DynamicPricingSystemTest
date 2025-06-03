# Dynamic Pricing System

A comprehensive dynamic pricing system that uses machine learning to optimize product prices based on various factors including historical sales data, inventory levels, competitor pricing, and customer ratings.

## Features

- Machine Learning-based price optimization
- Real-time competitor price monitoring
- Dynamic pricing adjustments based on business rules
- Interactive dashboard for monitoring and control
- Model performance tracking and visualization
- RESTful API for integration

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn

## Setup Instructions

### Backend Setup

1. Navigate to the project root directory
2. Run the setup script:
   - For Windows: `setup.bat`
   - For Unix/Linux/Mac: `./setup.sh`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/Linux/Mac: `source venv/bin/activate`
4. Start the Flask server:
   ```bash
   python run.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm start
   ```

## Project Structure

```
├── backend/
│   ├── controllers/
│   ├── models/
│   ├── services/
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.js
│   └── package.json
├── models/
├── logs/
├── requirements.txt
└── README.md
```

## API Documentation

### Pricing Endpoints

- `POST /api/pricing/optimize` - Optimize prices for all products
- `POST /api/pricing/product/<id>/optimize` - Optimize price for a specific product
- `PUT /api/pricing/product/<id>/price` - Update product price manually
- `GET /api/pricing/product/<id>/history` - Get pricing history
- `GET /api/pricing/competitor-prices` - Get competitor prices
- `GET /api/pricing/analytics` - Get pricing analytics

### Model Endpoints

- `POST /api/pricing/model/train` - Train or retrain the ML model
- `GET /api/pricing/model/info` - Get model information and metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.