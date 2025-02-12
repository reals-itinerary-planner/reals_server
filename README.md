# Reals Server

A modern FastAPI-based server application for managing GPT conversations with SQLAlchemy and PostgreSQL.

## Features

- 🚀 FastAPI for high-performance async API
- 🔐 User authentication and session management
- 🤖 GPT integration with conversation tracking
- 📊 API usage monitoring and logging
- 🗄️ PostgreSQL database with SQLAlchemy ORM
- 🔄 Async database operations
- 📝 Comprehensive API documentation (Swagger/OpenAPI)

## Environment Setup

The application supports multiple environments:

- Development (Local)
- Test (Render.com)
- Production

### Prerequisites

- Python 3.8+
- PostgreSQL
- pip

### Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd reals-server
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Local development
cp .env.example .env

# Test environment
cp .env.test.example .env.test
```

### Database Configuration

#### Local Development
```bash
# Start PostgreSQL service
# Create local database
createdb reals
```

#### Test Environment (Render.com)
1. Create a PostgreSQL database on Render.com
2. Update `.env.test` with Render.com credentials

### Running Migrations

```bash
# Initialize migrations (first time only)
alembic init alembic

# Create new migration
alembic revision --autogenerate -m "migration message"

# Apply migrations
alembic upgrade head
```

### Running the Application

```bash
# Development
uvicorn app.main:app --reload

# Test
ENV=test uvicorn app.main:app
```

## API Documentation

Once the server is running, access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
reals-server/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   └── services/
├── alembic/
├── tests/
├── .env
├── .env.test
└── requirements.txt
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[Your chosen license]

## Contact

[Your contact information]