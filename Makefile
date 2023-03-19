APPS = app bot

env:
	@$(eval SHELL:=/bin/bash)
	@cp .env.sample .env

lint:
	pylint $(APPS)

format:
	isort $(APPS)
	black $(APPS)