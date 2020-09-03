.PHONY: test install lint generate-tests-from-features

#include .env-dev

BUILD_PRINT = \e[1;34mSTEP: \e[0m

install:
	@ echo "$(BUILD_PRINT)Installing the requirements"
	@ pip install --upgrade pip
	@ pip install -r requirements.txt
	@ pip install -r requirements-dev.txt
	@ docker pull tinkerpop/gremlin-server

lint:
	@ echo "$(BUILD_PRINT)Linting the code"
	@ flake8 || true

test:
	@ echo "$(BUILD_PRINT)Running the tests"
	@ pytest



start-gremlin:
	@ echo "$(BUILD_PRINT)Starting Test Gremlin server"
	@ docker run -d --name gremlin-server -p 8182:8182 tinkerpop/gremlin-server

stop-gremlin:
	@ echo "$(BUILD_PRINT)Stopping Test Gremlin server"
	@ docker stop gremlin-server || true
	@ docker rm gremlin-server || true