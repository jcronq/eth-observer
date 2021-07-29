.PHONY: all

docker-build:
	docker build -t eth-observer .

docker-run: docker-build
	docker run --rm -p 9090:8000 --name eth-observer test-observer
