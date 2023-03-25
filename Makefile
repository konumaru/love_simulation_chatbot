.PHONY: init
init:
	docker compose run \
		--entrypoint "poetry init \
		--name app \
		--dependency fastapi \
		--dependency uvicorn[standard]" \
		app


.PHONY: install
install:
	docker compose run \
		--entrypoint "poetry install --no-root" \
		app
	docker compose exec app poetry -D \
		aiosqlite \
		httpx

.PHONY: up
up:
	docker compose up


.PHONY: test
test:
	docker-compose run --entrypoint "poetry run pytest" app
