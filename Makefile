.PHONY: up down restart logs ps clean health shell-app shell-db

# Start all services in background
up:
	docker compose up -d --build

# Stop all services
down:
	docker compose down

# Restart everything (rebuild)
restart: down up

# Follow logs from all services
logs:
	docker compose logs -f

# Show running containers
ps:
	docker compose ps

# Stop and remove volumes (full reset, destroys data!)
clean:
	docker compose down -v

# Quick health check — app and database
health:
	@echo "=== App ===" && curl -sf http://localhost/health && echo
	@echo "=== DB  ===" && curl -sf http://localhost/db/health && echo

# Shell into the app container
shell-app:
	docker compose exec app sh

# Open psql in the database container
shell-db:
	docker compose exec db psql -U $${DB_USER} -d $${DB_NAME}
