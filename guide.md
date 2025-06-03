# Dynamic Pricing System Test

## Objective:
The goal of this project is to demonstrate your ability to design and construct a comprehensive system that integrates advanced technologies, including AI-driven decision-making, front-end and back-end development, and complex algorithmic implementations with real-world business logic. This test evaluates your skills in system architecture, technology integration, and problem-solving in a business context.

## Problem Statement
You are tasked with building an end-to-end Dynamic Pricing System for an eCommerce platform. The system should enable real-time price adjustments based on historical data, market trends, competitor analysis, and business rules.
Your solution must integrate:
1.A Machine Learning Component for price prediction and optimization.
2.A Back-End API for managing product data and processing dynamic pricing.
3.A Front-End Dashboard for visualizing price changes, inventory status, and market insights.

## Requirements
### 1. System Features
1.
Dynamic Pricing Algorithm:
• Adjust prices dynamically based on:
• Historical sales trends.
• Inventory levels.
• Competitor pricing.
• Customer ratings and reviews.
• Apply multi-objective optimization to:
• Maximize revenue.
• Maintain competitive pricing.
• Minimize excess inventory.
### 2.
Machine Learning Integration:
• Train a model to predict optimal pricing based on historical data and market
conditions.
• Incorporate feature importance (e.g., demand elasticity, seasonal trends) in pricing decisions.
### 3.
Business Logic Rules:
• Override AI-predicted prices when:
• Inventory falls below a critical threshold (e.g., increase price by up to 30%).
• A competitor undercuts pricing significantly (e.g., reduce price by up to 20%, ensuring minimum profit margins).
• The system must ensure all prices remain:
• Above cost price + 10% (profit margin threshold).
• Below base price + 50%.
### 4.
Front-End Dashboard:
• A user-friendly interface to display:
• Product catalog with current and adjusted prices.
• Sales and inventory trends.
• Competitor price comparisons.
• Include interactive charts to visualize the impact of pricing adjustments.
### 5.
Back-End API:
• Provide RESTful endpoints for:
• Fetching product data.
• Processing pricing adjustments.
• Integrating with external data sources (e.g., competitor pricing API).
### 6.
Scalability:
• Ensure the system can handle datasets with 100,000+ products efficiently.
• Optimize data processing and API response times.

## Implementation Details
### 1. Input Data
• Product Catalog:
• product_id, base_price, inventory, sales_last_30_days, average_rating, category.
• Historical Sales Data:
• A time-series dataset of sales transactions.
• Competitor Pricing Data:
• Simulate fetching real-time competitor prices via a provided API.
### 2. Output
• Adjusted prices for each product, adhering to both AI predictions and business rules.
• A front-end dashboard displaying pricing insights.
### 3. Mock Competitor Pricing API
Endpoint: https://mock-api.com/competitor-prices
Response format:
[
{"product_id": "P001", "competitor_price": 90.0},
{"product_id": "P002", "competitor_price": 195.0},
{"product_id": "P003", "competitor_price": 48.0}
]

## Deliverables
### 1. Code Implementation
• Back-End API:
• A robust API built with a modern framework (e.g., Express.js, Flask, Django).
• Endpoints for CRUD operations and pricing logic integration.
• Machine Learning:
• Train and integrate a regression or optimization model for price prediction.
• Include a detailed report on model performance (e.g., accuracy, RMSE, feature importance).
• Front-End Dashboard:
• A responsive web app using React, Vue, or Angular for visualization.
### 2. Documentation
• README.md with:
• System architecture and design choices.
• Instructions for setting up and running the system.
• Documentation for API endpoints and ML pipeline.
### 3. Testing
• Comprehensive unit and integration tests.
• Include test cases for:
• Algorithm correctness.
• Business rule overrides.
• API endpoint responses.
### 4. Deployment
• Optional but encouraged: Deploy the system using Docker or a cloud platform (AWS/GCP/Azure).
• Provide a hosted link to the live system, if possible.

## Evaluation Criteria
### 1.
Technical Excellence:
• Quality of the machine learning model and system architecture.
• Robustness and scalability of the implementation.
### 2.
Business Logic Integration:
• Ability to translate real-world business scenarios into system functionality.
### 3.
Creativity:
• Innovative approaches to problem-solving and system design.
### 4.
User Experience:
• Intuitive and visually appealing front-end design.
### 5.
Documentation and Testing:
• Clear, thorough documentation and strong test coverage.

## Sample Dataset
### 1. Product Catalog:
[
{"product_id": "P001", "base_price": 100.0, "inventory": 15, "sales_last_30_days": 120, "average_rating": 4.5, "category": "Electronics"},
{"product_id": "P002", "base_price": 200.0, "inventory": 50, "sales_last_30_days": 40, "average_rating": 4.0, "category": "Apparel"},
{"product_id": "P003", "base_price": 50.0, "inventory": 5, "sales_last_30_days": 10, "average_rating": 3.8, "category": "Home"}
]
### 2. Historical Sales Data:
product_id,date,units_sold,price
P001,2024-10-01,5,95.0
P001,2024-10-02,10,90.0
P002,2024-10-01,3,190.0
P003,2024-10-01,1,48.0
Submission Guidelines
• Submit your solution as a GitHub repository or a compressed file.
• Include all deliverables (code, documentation, test cases).
We look forward to seeing your technical capabilities and innovative solutions to this challenging project. Good luck!