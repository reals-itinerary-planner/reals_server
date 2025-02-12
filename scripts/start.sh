#!/bin/bash

# Default to development if ENVIRONMENT not set
ENVIRONMENT=${ENVIRONMENT:-development}
export ENVIRONMENT=$ENVIRONMENT

# Load environment-specific settings
if [ -f ".env.$ENVIRONMENT" ]; then
    source ".env.$ENVIRONMENT"
fi

PORT=${PORT:-8000}
WORKERS=${WORKERS:-4}

# Add packages to Python path
export PYTHONPATH=dist/packages:$PYTHONPATH

echo "Starting server in $ENVIRONMENT mode..."

if [ "$ENVIRONMENT" = "production" ]; then
    # Production mode with Gunicorn
    gunicorn app.main:app \
        --chdir dist \
        --workers $WORKERS \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:$PORT \
        --access-logfile - \
        --error-logfile - \
        --log-level debug \
        --timeout 120
else
    # Development/Test mode with Uvicorn directly
    cd dist && python -m uvicorn app.main:app \
        --host 0.0.0.0 \
        --port $PORT \
        --reload \
        --log-level debug
fi 