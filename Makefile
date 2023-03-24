APPS = app bot
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

test:
	$(TEST)
