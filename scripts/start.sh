#!/bin/bash

# Default to development if ENV not set
ENV=${ENV:-development}
export ENV=$ENV

# Load environment-specific settings
if [ -f ".env.$ENV" ]; then
    source ".env.$ENV"
fi

PORT=${PORT:-8000}
WORKERS=${WORKERS:-4}

# Add packages to Python path
export PYTHONPATH=dist/packages:$PYTHONPATH

if [ "$ENV" = "development" ]; then
    # Development mode
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $PORT
else
    # Production/Test mode
    gunicorn app.main:app \
        --chdir dist \
        --workers $WORKERS \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:$PORT \
        --access-logfile - \
        --error-logfile - \
        --log-level info
fi 