.PHONY: build test test-fulltrace start stop restart clean deploy

build:
	docker build --rm=true -t simplewebcrawler_webcrawler .

test:
	docker-compose run --rm webcrawler python3 -m pytest

test-fulltrace:
	docker-compose run --rm webcrawler python3 -m pytest --fulltrace

start:
	docker-compose up -d

stop:
	-docker-compose kill && docker ps -a | grep simplewebcrawler_webcrawler | awk '{print $$1}' | xargs docker rm -fv

restart: stop start

clean:
	-docker-compose kill && docker ps -a | grep simplewebcrawler_webcrawler | awk '{print $$1}' | xargs docker rm -fv
	-docker rmi "simplewebcrawler_webcrawler"

deploy: clean
	docker-compose --file docker-compose-prod.yml build
	@echo "TODO: Actually deploy"
	docker-compose --file docker-compose-prod.yml up -d
