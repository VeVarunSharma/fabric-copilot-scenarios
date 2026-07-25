PYTHON ?= python3
FABRIC_CAPACITY_CONFIG ?= scripts/fabric/capacity.local.json
FABRIC_CAPACITY = $(PYTHON) scripts/fabric/capacity.py --config $(FABRIC_CAPACITY_CONFIG)

.PHONY: configure doctor deploy up down status fabric-configure fabric-doctor \
	fabric-deploy fabric-up fabric-down fabric-status fabric-connect fabric-destroy

configure: fabric-configure

doctor: fabric-doctor

deploy: fabric-deploy

up: fabric-up

down: fabric-down

status: fabric-status

fabric-configure:
	@if [ -e "$(FABRIC_CAPACITY_CONFIG)" ]; then \
		echo "$(FABRIC_CAPACITY_CONFIG) already exists"; \
	else \
		cp scripts/fabric/capacity.example.json "$(FABRIC_CAPACITY_CONFIG)"; \
		echo "Created $(FABRIC_CAPACITY_CONFIG)"; \
	fi

fabric-doctor:
	$(FABRIC_CAPACITY) doctor

fabric-deploy:
	$(FABRIC_CAPACITY) deploy

fabric-up:
	$(FABRIC_CAPACITY) up

fabric-down:
	$(FABRIC_CAPACITY) down

fabric-status:
	$(FABRIC_CAPACITY) status

fabric-connect:
	$(FABRIC_CAPACITY) connect

fabric-destroy:
	$(FABRIC_CAPACITY) destroy
