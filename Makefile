.PHONY: help install test run docker-build docker-run clean

help:
	@echo "HTML2PDF Service - Available Commands"
	@echo ""
	@echo "  make install       - Install dependencies"
	@echo "  make install-dev   - Install dev dependencies"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage"
	@echo "  make run           - Run development server"
	@echo "  make worker        - Run Celery worker"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run with docker-compose"
	@echo "  make docker-down   - Stop docker-compose"
	@echo "  make clean         - Clean generated files"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"

install:
	pip install -r requirements.txt
	playwright install chromium

install-dev:
	pip install -r requirements.txt
	pip install black flake8 mypy
	playwright install chromium

test:
	pytest

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

test-unit:
	pytest -m unit

test-integration:
	pytest -m integration

run:
	python app.py

worker:
	celery -A celery_worker.celery_app worker --loglevel=info

docker-build:
	docker build -t html2pdf:latest .

docker-run:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov dist build
	rm -f *.pdf

lint:
	flake8 app/ tests/ --max-line-length=120
	mypy app/ --ignore-missing-imports

format:
	black app/ tests/ --line-length=120

# Kubernetes deployment
k8s-deploy:
	kubectl apply -f deployment/kubernetes/

k8s-delete:
	kubectl delete namespace html2pdf

# Development helpers
redis:
	docker run -d -p 6379:6379 redis:7-alpine

flower:
	celery -A celery_worker.celery_app flower --port=5555
