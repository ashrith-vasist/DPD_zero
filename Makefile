IMAGE_NAME = dpd-zero
CONTAINER_NAME = dpd-container 

build_docker:
	@docker build -t $(IMAGE_NAME) .

run_docker: 
	@docker run -d -p 5000:5000 --name $(CONTAINER_NAME) $(IMAGE_NAME)

stop_dcoker:
	@docker stop $(CONTAINER_NAME)

remove_docker:
	@docker remove $(CONTAINER_NAME)

removei_docker:
	@docker rmi $(IMAGE_NAME)

virtualenv:
	@python3 -m venv .venv

activate:
	@source .venv/bin/activate

install:
	@pip install -r requirements.txt

run:
	@python3 src/app.py runserver

deactviate:
	@deactivate

clean:
	@rm -rf .venv

.PHONY: build run stop remove removei