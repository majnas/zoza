.PHONY: build install lint test bilt

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
	docker exec -it $(CONTAINER_NAME) bash -c "pylint --disable=R,C zoza/*.py"

test:
	docker exec -it $(CONTAINER_NAME) bash -c "python -m pytest tests/ -v --cache-clear"

cleanup:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

cbilt:  
	@echo "Running build, install, lint, and test..."
	@make -s cleanup
	@make -s build  
	@make -s install  
	@make -s lint  
	@make -s test
