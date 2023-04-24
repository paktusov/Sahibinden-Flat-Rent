APPS = app bot storage tests
TEST = pytest --verbosity=2 --showlocals --log-level=DEBUG

env:
	@$(eval SHELL:=/bin/bash)
	@cp .env.sample .env

lint:
	pylint $(APPS)

format:
	isort $(APPS)
	black $(APPS)

start_mongo:
	docker-compose up -d mongo

stop_mongo:
	docker-compose down

start_postgres:
	docker-compose up -d postgres

stop_postgres:
	docker-compose down

upgrade_db:
	docker-compose up -d mongo postgres bot
	docker exec -i $$(docker ps | grep bot | cut -d ' ' -f 1) alembic upgrade b9d4fb17eb8d
	docker exec -i $$(docker ps | grep bot | cut -d ' ' -f 1) alembic upgrade 50e8142ee506
	docker-compose down


downgrade_db:
	docker-compose up -d mongo postgres bot
	docker exec -i $$(docker ps | grep bot | cut -d ' ' -f 1) alembic downgrade base
	docker-compose down

test:
	$(TEST)
