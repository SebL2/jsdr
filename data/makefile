PKG = data
TEST_PATH = ../server/tests

include ../common.mk

pytests: FORCE
	pytest $(PYTESTFLAGS) --cov=$(PKG) $(TEST_PATH)
