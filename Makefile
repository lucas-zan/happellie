SHELL := /bin/bash

ROOT_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
BACKEND_DIR := $(ROOT_DIR)/backend
FRONTEND_DIR := $(ROOT_DIR)/frontend

PYTHON ?= python3
PIP ?= pip
NPM ?= npm
NPM_REGISTRY ?= https://registry.npmjs.org/

.PHONY: help bootstrap bootstrap-backend bootstrap-frontend ensure-backend ensure-frontend backend frontend dev smoke

help:
	@echo "Available targets:"
	@echo "  make bootstrap          Install backend and frontend dependencies"
	@echo "  make backend            Start the FastAPI backend"
	@echo "  make frontend           Start the Vite frontend"
	@echo "  make dev                One-command local run for backend + frontend"
	@echo "  make smoke              Run the backend smoke test"

bootstrap: bootstrap-backend bootstrap-frontend

bootstrap-backend:
	@cd "$(BACKEND_DIR)" && \
		$(PYTHON) -m venv .venv && \
		. .venv/bin/activate && \
		$(PIP) install -r requirements.txt && \
		cp -n .env.example .env || true && \
		python -m app.bootstrap

bootstrap-frontend:
	@cd "$(FRONTEND_DIR)" && \
		cp -n .env.example .env || true
	@if [ -f "$(FRONTEND_DIR)/package-lock.json" ] && grep -q 'packages\.applied-caas-gateway1\.internal\.api\.openai\.org' "$(FRONTEND_DIR)/package-lock.json"; then \
		echo "[WARN] frontend/package-lock.json points to an internal registry; installing without lockfile"; \
		cd "$(FRONTEND_DIR)" && $(NPM) install --no-package-lock --registry="$(NPM_REGISTRY)"; \
	else \
		cd "$(FRONTEND_DIR)" && $(NPM) install; \
	fi

ensure-backend:
	@if [ ! -d "$(BACKEND_DIR)/.venv" ]; then \
		$(MAKE) bootstrap-backend; \
	else \
		cd "$(BACKEND_DIR)" && cp -n .env.example .env || true; \
	fi

ensure-frontend:
	@if [ ! -d "$(FRONTEND_DIR)/node_modules" ]; then \
		$(MAKE) bootstrap-frontend; \
	else \
		cd "$(FRONTEND_DIR)" && cp -n .env.example .env || true; \
	fi

backend: ensure-backend
	@./scripts/run_backend.sh

frontend: ensure-frontend
	@./scripts/run_frontend_web.sh

dev: ensure-backend ensure-frontend
	@./scripts/run_local_app.sh

smoke: ensure-backend
	@./scripts/smoke_test.sh
