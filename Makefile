# AEGIS — top-level orchestration.
#
# This repository spans four toolchains that do not share a package manager:
#   * ROS 2 / colcon  (autonomy)
#   * pip / Python    (perception, services)
#   * pnpm / Node     (web)
#   * PlatformIO      (firmware)
# The Makefile is the single entry point so that "how do I run this" has one
# answer regardless of which corner of the tree you are standing in.

SHELL := /bin/bash
.DEFAULT_GOAL := help
.ONESHELL:

ROOT       := $(shell pwd)
COMPOSE    := docker compose -f infra/compose/docker-compose.yml
ROS_DISTRO ?= jazzy
PY         := python3

# Colours, disabled when stdout is not a TTY so CI logs stay clean.
ifneq ($(shell test -t 1 && echo tty),)
  BOLD := $(shell tput bold)
  DIM  := $(shell tput dim)
  CYAN := $(shell tput setaf 6)
  OFF  := $(shell tput sgr0)
endif

##@ General

.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\n$(BOLD)AEGIS$(OFF) — autonomous aerial security\n\nUsage:\n  $(CYAN)make$(OFF) $(DIM)<target>$(OFF)\n"} \
	  /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(CYAN)%-22s$(OFF) %s\n", $$1, $$2 } \
	  /^##@/ { printf "\n$(BOLD)%s$(OFF)\n", substr($$0, 5) }' $(MAKEFILE_LIST)
	@echo

.PHONY: doctor
doctor: ## Check that the required toolchains are present
	@bash tools/doctor.sh

##@ Setup

.PHONY: setup
setup: setup-python setup-web ## Bootstrap every toolchain

.PHONY: setup-python
setup-python: ## Create the Python virtualenv and install dependencies
	@$(PY) -m venv .venv
	@. .venv/bin/activate && pip install --quiet --upgrade pip && pip install -e '.[dev]'

.PHONY: setup-web
setup-web: ## Install web dependencies
	@cd web && pnpm install --frozen-lockfile

##@ Simulation

.PHONY: sim
sim: ## Launch Gazebo + PX4 SITL in the residential-society world
	@bash sim/scripts/launch.sh

.PHONY: sim-headless
sim-headless: ## Launch simulation without the Gazebo GUI (for CI / batch runs)
	@HEADLESS=1 bash sim/scripts/launch.sh

##@ Autonomy (ROS 2)

.PHONY: autonomy-build
autonomy-build: ## colcon build the autonomy workspace
	@cd autonomy && source /opt/ros/$(ROS_DISTRO)/setup.bash && colcon build --symlink-install

.PHONY: autonomy-test
autonomy-test: ## Run the autonomy test suite
	@cd autonomy && source /opt/ros/$(ROS_DISTRO)/setup.bash && colcon test && colcon test-result --verbose

##@ Perception (ML)

.PHONY: data
data: ## Download and prepare the aerial datasets
	@. .venv/bin/activate && $(PY) -m perception.datasets.prepare

.PHONY: train
train: ## Train the detector
	@. .venv/bin/activate && $(PY) -m perception.training.train

.PHONY: eval
eval: ## Evaluate the detector and write the benchmark report
	@. .venv/bin/activate && $(PY) -m perception.eval.benchmark

.PHONY: export
export: ## Export the detector to ONNX / TensorRT
	@. .venv/bin/activate && $(PY) -m perception.export.to_onnx

##@ Services (backend)

.PHONY: up
up: ## Start the full backend stack
	@$(COMPOSE) up -d --build

.PHONY: down
down: ## Stop the backend stack
	@$(COMPOSE) down

.PHONY: logs
logs: ## Tail backend logs
	@$(COMPOSE) logs -f --tail=100

##@ Web

.PHONY: web
web: ## Run the operations dashboard in dev mode
	@cd web && pnpm dev

##@ Firmware

.PHONY: firmware
firmware: ## Build all ESP32 firmware targets
	@cd firmware && pio run

##@ Quality

.PHONY: lint
lint: ## Lint everything
	@bash tools/lint.sh

.PHONY: fmt
fmt: ## Auto-format everything
	@bash tools/format.sh

.PHONY: test
test: ## Run every test suite
	@bash tools/test.sh

##@ Documents

.PHONY: paper
paper: ## Build the IEEE paper PDF
	@$(MAKE) -C paper

.PHONY: clean
clean: ## Remove build artefacts
	@rm -rf autonomy/build autonomy/install autonomy/log web/dist .pytest_cache .ruff_cache
	@find . -name '__pycache__' -type d -prune -exec rm -rf {} +
