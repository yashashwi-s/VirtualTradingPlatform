# Virtual Trading Platform

A comprehensive virtual trading platform built with FastAPI backend and Next.js frontend.

## Features

### Backend (FastAPI)
- 🔐 JWT-based user authentication
- 📊 Virtual portfolio management with $100,000 starting balance
- 📈 Real-time market data integration (Alpha Vantage API)
- ⚡ Redis caching for optimized performance
- 🏪 Buy/sell order execution engine
- 📋 PostgreSQL database with comprehensive schemas
- 🔄 RESTful API design with auto-generated documentation

### Frontend (Next.js)
- ⚛️ Modern React-based UI with TypeScript
- 🎨 Tailwind CSS for responsive design
- 📱 Mobile-friendly trading dashboard
- 📊 Portfolio overview with P&L tracking
- 💹 Interactive trading interface
- 🔍 Stock symbol search functionality
- 📈 Real-time quote updates

### Database Schema
- **Users**: Authentication and profile management
- **Portfolios**: Multiple portfolio support per user
- **Positions**: Current stock holdings tracking
- **Trades**: Complete transaction history
- **Market Data**: Cached stock information

## Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/yashashwi-s/VirtualTradingPlatorm.git
   cd VirtualTradingPlatorm
   ```

2. **Set up environment variables**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   
   # Frontend
   cp frontend/.env.example frontend/.env
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Manual Setup

### Backend Setup

1. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL and Redis**
   - Install PostgreSQL and Redis locally
   - Create a database named `trading_platform`
   - Update database credentials in `.env`

3. **Run the backend**
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. **Install Node.js dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Run the development server**
   ```bash
   npm run dev
   ```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user profile

### Portfolio Management
- `GET /api/v1/portfolios` - Get user portfolios
- `POST /api/v1/portfolios` - Create new portfolio
- `GET /api/v1/portfolios/{id}/positions` - Get portfolio positions
- `GET /api/v1/portfolios/{id}/summary` - Get portfolio summary

### Trading
- `POST /api/v1/trades` - Place buy/sell order
- `GET /api/v1/trades` - Get user trade history
- `GET /api/v1/trades/{id}` - Get specific trade details

### Market Data
- `GET /api/v1/market/quote/{symbol}` - Get real-time stock quote
- `GET /api/v1/market/intraday/{symbol}` - Get intraday chart data
- `GET /api/v1/market/search` - Search stock symbols

## Environment Variables

### Backend (.env)
```
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=trading_platform
REDIS_HOST=localhost
REDIS_PORT=6379
SECRET_KEY=your-secret-key
ALPHA_VANTAGE_API_KEY=your-api-key
```

### Frontend (.env)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Technology Stack

**Backend:**
- FastAPI - Modern Python web framework
- SQLAlchemy - ORM with async support
- PostgreSQL - Primary database
- Redis - Caching layer
- Alpha Vantage - Market data provider
- JWT - Authentication tokens

**Frontend:**
- Next.js - React framework
- TypeScript - Type safety
- Tailwind CSS - Utility-first styling
- React Query - Data fetching
- React Hook Form - Form management
- Heroicons - Icon library

**Infrastructure:**
- Docker - Containerization
- Docker Compose - Multi-container orchestration

## Development Features

- 🔄 Hot reload for both frontend and backend
- 📝 Auto-generated API documentation (FastAPI/Swagger)
- 🧪 Database migrations with Alembic
- 🔒 Secure password hashing
- 📊 Redis-based caching strategy
- ✅ Input validation with Pydantic

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.