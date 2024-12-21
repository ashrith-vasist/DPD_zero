IMAGE_NAME = dpd-zero
CONTAINER_NAME = dpd-container 

# Build Docker image
build_docker:
	@docker build -t $(IMAGE_NAME) .

# Run Docker container
run_docker: 
	@docker run -d -p 5000:5000 --name $(CONTAINER_NAME) $(IMAGE_NAME)

# Stop Docker container
stop_docker:
	@docker stop $(CONTAINER_NAME)

# Remove Docker container
remove_docker:
	@docker rm $(CONTAINER_NAME)

# Remove Docker image
remove_image:
	@docker rmi $(IMAGE_NAME)

virtualenv:
	python3 -m venv .venv
	@echo "\nVirtual environment created. Now run:"
	@echo "  source .venv/bin/activate  (Linux/Mac)"
	@echo "  .\.venv\Scripts\activate   (Windows)"

install:
	pip install -r requirements.txt

start:
	python3 src/app.py

# Clean up virtual environment
clean:
	@rm -rf .venv

.PHONY: build_docker run_docker stop_docker remove_docker remove_image virtualenv activate install run deactivate clean
