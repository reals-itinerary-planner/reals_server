#!/bin/bash

# Default to development if ENV not set
ENV=${ENV:-development}
export ENV=$ENV

# Load ENV-specific settings
if [ -f ".env.$ENV" ]; then
    source ".env.$ENV"
fi

PORT=${PORT:-8000}
WORKERS=${WORKERS:-4}

echo "Starting server in $ENV mode... PORT: $PORT, WORKERS: $WORKERS"

# Change to dist directory and ensure dependencies are installed
cd dist || exit 1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --no-cache-dir

if [ "$ENV" = "production" ]; then
    # Production mode with Gunicorn
    python -m gunicorn app.main:app \
        --workers $WORKERS \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:$PORT \
        --access-logfile - \
        --error-logfile - \
        --log-level debug \
        --timeout 120
else
    # Development/Test mode with Uvicorn directly
    python -m uvicorn app.main:app \
        --host 0.0.0.0 \
        --port $PORT \
        --reload \
        --log-level debug
fi 