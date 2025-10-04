#!/bin/bash
# Quick Start Script for Development

echo "========================================"
echo "Oracle AWR Report Analyzer - Dev Setup"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

echo "${GREEN}✓${NC} Docker is running"
echo ""

# Start database services
echo "Starting PostgreSQL and Redis..."
docker-compose up -d postgres redis

# Wait for services
echo "Waiting for services to be ready..."
sleep 5

echo "${GREEN}✓${NC} Database services started"
echo ""

# Setup backend
echo "Setting up backend..."
cd backend

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

# Create uploads directory
mkdir -p uploads

# Initialize database
echo "Initializing database..."
python -c "from app.models import Base, engine; Base.metadata.create_all(engine)"

echo "${GREEN}✓${NC} Backend setup complete"
echo ""

# Instructions
echo "========================================"
echo "Setup Complete! Next Steps:"
echo "========================================"
echo ""
echo "1. Start Backend API:"
echo "   ${YELLOW}cd backend && uvicorn app.main:app --reload${NC}"
echo ""
echo "2. Start Celery Worker (in new terminal):"
echo "   ${YELLOW}cd backend && celery -A app.tasks.celery_app worker --loglevel=info${NC}"
echo ""
echo "3. Test Parser:"
echo "   ${YELLOW}cd backend && python test_parser.py${NC}"
echo ""
echo "4. Access API Documentation:"
echo "   ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
echo "5. Test Upload (after starting backend):"
echo "   ${YELLOW}curl -X POST http://localhost:8000/api/v1/reports/upload -F \"file=@awrrpt/19c/awrrpt_1_17676_17677.html\"${NC}"
echo ""
echo "========================================"
