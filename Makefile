
.PHONY: build install lint test bilt

# Load environment variables from .env file
include .env

# Export all variables from .env to be available in subprocesses
export


build:
	docker build -t $(IMAGE_NAME) .

install:
	docker run -dit --name $(CONTAINER_NAME) -v $(PWD):/app -w /app $(IMAGE_NAME) bash
	docker exec -it $(CONTAINER_NAME) bash -c "pip install --upgrade pip && pip install -r zoza/requirements.txt"

lint:
	docker exec -it $(CONTAINER_NAME) bash -c "pylint --disable=R,C zoza/*.py"

test:
	docker exec -it $(CONTAINER_NAME) bash -c "python -m pytest tests/ --durations=0 -v -W ignore::DeprecationWarning -W ignore::UserWarning"

cleanup:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

bilt:  
	@echo "Running build, install, lint, and test..."
	make build  
	make install  
	make lint  
	make test