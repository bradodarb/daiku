.PHONY: lint test typecheck ci dev-up dev-down

lint:
	ruff check daiku tests

test:
	pytest

typecheck:
	mypy daiku tests

ci: lint typecheck test

dev-up:
	docker compose up -d

dev-down:
	docker compose down
