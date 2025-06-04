# Dynamic Pricing System

A comprehensive dynamic pricing system that uses machine learning to optimize product prices based on various factors including historical sales data, inventory levels, competitor pricing, and customer ratings.

## System Architecture

### Overview
The system follows a modern microservices architecture with the following components:

```
├── Frontend (React)
│   ├── Dashboard
│   ├── Product Management
│   └── Analytics
├── Backend (Flask)
│   ├── API Layer
│   ├── Business Logic
│   └── Data Access
└── ML Pipeline
    ├── Data Processing
    ├── Model Training
    └── Price Prediction
```

### Key Components

1. **Frontend**
   - React-based single-page application
   - Material-UI for consistent design
   - Redux for state management
   - Real-time updates using WebSocket

2. **Backend**
   - Flask RESTful API
   - SQLAlchemy ORM
   - JWT Authentication
   - Redis caching layer

3. **ML Pipeline**
   - XGBoost for price prediction
   - Feature engineering pipeline
   - Model versioning and monitoring
   - Automated retraining

### Design Choices

1. **Technology Stack**
   - Frontend: React + TypeScript for type safety and maintainability
   - Backend: Flask for lightweight and flexible API development
   - Cache: Redis for high-performance caching
   - ML: XGBoost for efficient gradient boosting

2. **Architecture Decisions**
   - Microservices for scalability and maintainability
   - RESTful API for standardized communication
   - Event-driven architecture for real-time updates
   - Containerization for easy deployment

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
- Docker and Docker Compose (for containerized deployment)

## Setup Instructions

### Option 1: Local Development Setup

#### Backend Setup

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

#### Frontend Setup

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

### Option 2: Docker Deployment

The system can be deployed using Docker containers. This is the recommended approach for production environments.

1. **Build and Start Containers**
   ```bash
   docker-compose up --build
   ```
   This will:
   - Build the backend container using Python 3.10
   - Build the frontend container using Node.js 18
   - Start both services with the following ports:
     - Backend: http://localhost:5000
     - Frontend: http://localhost:3000

2. **Stop Containers**
   ```bash
   docker-compose down
   ```

3. **View Logs**
   ```bash
   docker-compose logs -f
   ```

4. **Rebuild Specific Service**
   ```bash
   docker-compose up --build backend  # Rebuild and restart backend only
   docker-compose up --build frontend # Rebuild and restart frontend only
   ```

#### Docker Configuration Details

1. **Backend Container**
   - Base Image: Python 3.10
   - Port: 5000
   - Environment Variables:
     - FLASK_ENV=production
     - FLASK_APP=run.py
   - Auto-restart: unless-stopped

2. **Frontend Container**
   - Build Stage: Node.js 18
   - Production Stage: Nginx Alpine
   - Port: 3000 (mapped to container port 80)
   - Auto-restart: unless-stopped

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
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
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