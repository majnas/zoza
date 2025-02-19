.PHONY: build install lint test cleanup bilt deploy run_bot

# Load environment variables from .env file
include .env

# Export all variables from .env to be available in subprocesses
export

build:
	docker build -t $(IMAGE_NAME) .

install:
	docker run -dit --name $(CONTAINER_NAME) -v $(PWD):/app -w /app $(IMAGE_NAME) bash
	docker exec -it $(CONTAINER_NAME) bash -c "pip install -r zoza/requirements.txt"

lint:
	docker exec -it $(CONTAINER_NAME) bash -c "pylint --disable=R,C,W0613 zoza/*.py"

test:
	docker exec -it $(CONTAINER_NAME) bash -c "python -m pytest tests/ -v --cache-clear"


up:
	docker exec -d $(CONTAINER_NAME) bash -c "supervisord -c /etc/supervisor/conf.d/supervisord.conf"
	

logs:
	docker exec -it $(CONTAINER_NAME) tail -f /app/zoza_err.log

down:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

deploy: down build install lint test up
