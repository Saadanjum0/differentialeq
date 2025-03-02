#!/bin/bash
set -e

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Building Docker image...${NC}"
docker-compose build

echo -e "${YELLOW}Starting Docker container...${NC}"
docker-compose up -d

echo -e "${GREEN}Docker container is running!${NC}"
echo -e "${GREEN}Access the application at: http://localhost:5001${NC}"
echo -e "${YELLOW}To view logs: ${NC}docker-compose logs -f"
echo -e "${YELLOW}To stop the container: ${NC}docker-compose down" 