#!/bin/bash

# Default to development if ENV not set
ENV=${ENV:-development}

# Build script
echo "Building application for $ENV environment..."

# Create dist directory if it doesn't exist
mkdir -p dist

# Copy necessary files to dist
cp -r app dist/
cp requirements.txt dist/
cp alembic.ini dist/
cp -r alembic dist/

# Copy environment-specific .env file
if [ -f ".env.$ENV" ]; then
    cp ".env.$ENV" dist/.env
    echo "Using .env.$ENV configuration"
else
    echo "Warning: .env.$ENV not found, using default .env"
    cp .env dist/.env
fi

# Install production dependencies
# if [ "$ENV" = "production" ]; then
    pip install -r requirements.txt --target dist/packages
# else
#     pip install -r requirements-dev.txt --target dist/packages
# fi

echo "Build completed in ./dist for $ENV environment" 