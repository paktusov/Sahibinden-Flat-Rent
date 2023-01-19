CODE = app bot
TEST = pytest --verbosity=2 --showlocals --log-level=DEBUG

env:
	@$(eval SHELL:=/bin/bash)
	@cp .env.sample .env

lint:
	pylint $(CODE)

format:
	isort $(CODE)
	black $(CODE)

start_db:
	docker-compose up -d mongo

stop_db:
	docker-compose down

test:
	$(TEST)
