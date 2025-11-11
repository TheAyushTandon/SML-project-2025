#!/bin/bash
echo "🚀 Starting FastAPI backend..."

# Ensure we're using Python 3 and pip
PYTHON=$(which python3 || which python)

# Install dependencies from requirements.txt
$PYTHON -m pip install --upgrade pip
$PYTHON -m pip install -r requirements.txt

# Move to backend folder
cd backend

# Start FastAPI using uvicorn (via Python)
$PYTHON -m uvicorn app:app --host 0.0.0.0 --port 8000
