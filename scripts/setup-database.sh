#!/bin/bash
# Database setup script for Mids Hero Web
# Handles both Docker and local PostgreSQL setups

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🗃️  Mids Hero Web Database Setup${NC}"
echo "============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Function to check if PostgreSQL is running locally
check_local_postgres() {
    if brew services list | grep -q "postgresql.*started"; then
        echo -e "${YELLOW}⚠️  Local PostgreSQL is running and may conflict with Docker.${NC}"
        echo "Would you like to stop it? (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            brew services stop postgresql@14 2>/dev/null || brew services stop postgresql@15 2>/dev/null || echo "Could not stop PostgreSQL"
            echo -e "${GREEN}✅ Local PostgreSQL stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  Continuing with local PostgreSQL running (may cause conflicts)${NC}"
        fi
    fi
}

# Function to start Docker database
start_docker_db() {
    echo -e "${GREEN}🐳 Starting Docker PostgreSQL...${NC}"
    
    # Stop any existing containers
    docker-compose down db 2>/dev/null || true
    
    # Start just the database service
    docker-compose up -d db
    
    # Wait for database to be ready
    echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
    timeout=30
    while [ $timeout -gt 0 ]; do
        if docker exec mids-hero-web-db-1 pg_isready -U postgres -d mids_web > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Database is ready!${NC}"
            break
        fi
        sleep 1
        timeout=$((timeout - 1))
    done
    
    if [ $timeout -eq 0 ]; then
        echo -e "${RED}❌ Database failed to start within 30 seconds${NC}"
        exit 1
    fi
}

# Function to run migrations
run_migrations() {
    echo -e "${GREEN}🚀 Running database migrations...${NC}"
    
    cd backend
    
    # Try Docker database first
    if DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mids_web uv run alembic upgrade head; then
        echo -e "${GREEN}✅ Migrations completed successfully!${NC}"
    else
        echo -e "${RED}❌ Migration failed${NC}"
        exit 1
    fi
    
    cd ..
}

# Function to verify database setup
verify_setup() {
    echo -e "${GREEN}🔍 Verifying database setup...${NC}"
    
    # Check if tables exist
    table_count=$(docker exec mids-hero-web-db-1 psql -U postgres -d mids_web -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null || echo "0")
    
    if [ "$table_count" -gt 0 ]; then
        echo -e "${GREEN}✅ Found $table_count tables in database${NC}"
        echo -e "${GREEN}📊 Database schema is ready!${NC}"
    else
        echo -e "${RED}❌ No tables found in database${NC}"
        exit 1
    fi
}

# Function to show database info
show_database_info() {
    echo -e "${GREEN}📋 Database Information:${NC}"
    echo "  Database URL: postgresql://postgres:postgres@localhost:5432/mids_web"
    echo "  Admin URL: http://localhost:8080 (Adminer)"
    echo "  Container: mids-hero-web-db-1"
    echo ""
    echo -e "${GREEN}🔧 Useful Commands:${NC}"
    echo "  Connect to database: docker exec -it mids-hero-web-db-1 psql -U postgres -d mids_web"
    echo "  Stop database: docker-compose down db"
    echo "  Reset database: docker-compose down db -v && ./scripts/setup-database.sh"
    echo "  Run migrations: cd backend && DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mids_web uv run alembic upgrade head"
}

# Main execution
main() {
    check_local_postgres
    start_docker_db
    run_migrations
    verify_setup
    show_database_info
    
    echo -e "${GREEN}🎉 Database setup completed successfully!${NC}"
    echo "You can now run 'just dev' to start the full development environment."
}

# Run main function
main "$@"