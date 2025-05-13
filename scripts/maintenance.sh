#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== System Maintenance Script ===${NC}"

# Check disk space
echo -e "\n${YELLOW}Checking disk space...${NC}"
df -h

# Check memory usage
echo -e "\n${YELLOW}Checking memory usage...${NC}"
free -h

# Check Docker disk usage
echo -e "\n${YELLOW}Checking Docker disk usage...${NC}"
docker system df

# Clean up Docker
echo -e "\n${YELLOW}Cleaning up Docker...${NC}"
docker system prune -f

# Clean up old logs
echo -e "\n${YELLOW}Cleaning up old logs...${NC}"
sudo find /var/log -type f -name "*.gz" -delete
sudo find /var/log -type f -name "*.old" -delete
sudo find /var/log -type f -name "*.1" -delete

# Clean up apt cache
echo -e "\n${YELLOW}Cleaning up apt cache...${NC}"
sudo apt-get clean
sudo apt-get autoremove -y

# Check system load
echo -e "\n${YELLOW}Checking system load...${NC}"
uptime

# Check running containers
echo -e "\n${YELLOW}Checking running containers...${NC}"
docker ps

# Check container resource usage
echo -e "\n${YELLOW}Checking container resource usage...${NC}"
docker stats --no-stream

echo -e "\n${GREEN}Maintenance completed!${NC}" 