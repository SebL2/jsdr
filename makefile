include common.mk

# Our directories
API_DIR = server
CITIES_DIR = cities
DB_DIR = data
SEC_DIR = security
REQ_DIR = .

FORCE:

prod: all_tests github

github: FORCE
	git add .
	- git commit -a
	git push origin master

all_tests: lint
	cd $(API_DIR) && make tests
	cd $(CITIES_DIR) && make tests
	cd $(DB_DIR) && make tests
	cd $(SEC_DIR) && make tests
	cd $(REQ_DIR) && make tests


dev_env: FORCE
	pip install -r $(REQ_DIR)/requirements-dev.txt
	@echo "You should set PYTHONPATH to: "
	@echo $(shell pwd)
# Run flake8 on all key directories
lint:
	@echo "Running flake8 lint checks..."
	flake8 $(API_DIR) $(CITIES_DIR) --exclude=__main__.py
	@echo "✓ flake8 passed!"


docs: FORCE
	cd $(API_DIR); make docs
