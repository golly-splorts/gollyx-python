SHELL=/bin/bash

ifeq ($(shell echo ${GOLLYX_PYTHON_HOME}),)
$(error Environment variable GOLLYX_PYTHON_HOME not defined. Please run "source environment" in the repo root directory before running make commands)
endif
